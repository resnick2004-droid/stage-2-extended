"""The C-007 confirmation test (T5). Runs ONCE, under its registered pre-registration.

    python scripts/confirm_c007.py

Refuses unless:
  * `config/c007.yaml` `confirmation.prereg_id` is a runnable row in prereg/REGISTRY.md
    (`PreregRegistry.require_runnable`, the harness's own check);
  * every frozen input still has the sha256 the pre-registration pinned
    (`config/c007_frozen.json`, written at registration);
  * all eight confirmation evidence files are ingested and the data-integrity report
    docs/data_reports/C007_confirmation_evidence.md has a verdict without BLOCK.

Then: frozen HAR from all development days -> confirmation trades (D-100's arithmetic) ->
`c007_confirm.verdict`. Writes results/c007_confirmation.csv (one row per statistic) and
results/c007_confirmation_trades.csv (every trade, with u).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.backtest.harness import PreregRegistry, VariantCounter  # noqa: E402
from propedge.data.run_kit import CONF_RUNS  # noqa: E402
from propedge.data.window import D144_DEVELOPMENT_END as DEVELOPMENT_END  # noqa: E402  (C-007's window, D-144)
from propedge.execution.fills import FillModel  # noqa: E402
from propedge.outcomes import c007_confirm as cc  # noqa: E402
from propedge.outcomes import time_exit_sd as tx  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

REPORT = ROOT / "docs" / "data_reports" / "C007_confirmation_evidence.md"
#: path -> sha256 of every frozen input, written at registration (c007.yaml cannot hold its own).
FROZEN = ROOT / "config" / "c007_frozen.json"


def _integrity_passed() -> bool:
    if not REPORT.is_file():
        return False
    text = REPORT.read_text(encoding="utf-8")
    return "## Verdict" in text and "BLOCK" not in text.split("## Verdict")[-1]


def _refuse(msg: str) -> int:
    print("REFUSED: " + msg)
    return 2


def main() -> int:
    cfg = tx.load_c007()
    conf = cfg["confirmation"]
    PreregRegistry.load().require_runnable(conf["prereg_id"])
    if not FROZEN.is_file():
        return _refuse(f"{FROZEN.relative_to(ROOT)} missing; registration pins the frozen inputs.")
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if "config/c007.yaml" not in frozen:
        return _refuse("config/c007.yaml is not among the frozen inputs.")
    for rel, want in frozen.items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != want:
            return _refuse(f"{rel} changed since registration.")
    ev = {}
    for m in tx.MARKETS:
        ev[m] = []
        for p in conf["parts"]:
            rid = CONF_RUNS[(m, p["part"])].split("-")[0]
            found = sorted((ROOT / "results").glob(f"manual_{rid}_*.csv"))
            if len(found) != 1:
                return _refuse(f"{m} part {p['part']}: expected one ingested {rid} file, found "
                               f"{len(found)}.")
            ev[m].append(str(found[0].relative_to(ROOT).as_posix()))
    if not _integrity_passed():
        return _refuse(f"no passing data-integrity verdict in {REPORT.relative_to(ROOT)}.")

    # 1. the frozen forecast, from development only
    dev = pd.concat([tx.load_evidence(m, cfg) for m in tx.MARKETS], ignore_index=True)
    fit = cc.fit_frozen_har(dev, lags=tuple(cfg["har"]["lags"]),
                            min_fit=cfg["har"]["min_fit_days_per_market"])

    # 2. the confirmation evidence, spliced after development for the forecast's lags
    overlap, conf_rows = {}, []
    for m in tx.MARKETS:
        parts = [(read_result(ROOT / path), *p["own"])
                 for path, p in zip(ev[m], conf["parts"])]
        joined, overlap[m] = cc.assemble_parts(parts)
        conf_rows.append(tx.window_filter(tx.prepare(joined, m), m))
    confp = pd.concat(conf_rows, ignore_index=True)
    if (confp["date"] < pd.Timestamp(DEVELOPMENT_END)).any():
        raise AssertionError("a development day reached the confirmation panel")
    panel = pd.concat([dev.assign(_conf=False), confp.assign(_conf=True)], ignore_index=True)
    panel["rvhat"] = cc.apply_frozen_har(panel, fit)

    # 3. the trades
    fm = FillModel.load("assumed")
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks,
            "flatten": fm.flatten_slippage_ticks}
    days = []
    for m in tx.MARKETS:
        leg = cfg["legs"][m]
        rows = panel[(panel["market"] == m) & panel["_conf"]].sort_values("date")
        days.append(tx.trades(rows, tx.vehicle(leg["vehicle"]), floor_ticks=leg["floor_ticks"],
                              multiplier=cfg["stop_multiplier"],
                              budget=cfg["leg_risk_budget_usd"], slip=slip))
    alld = pd.concat(days, ignore_index=True)
    traded = alld[alld["reason"] == ""]

    # 4. the verdict -- one call, recorded as the pre-registration's one variant
    params = {"config": "config/c007.yaml", "c007_source": cfg["source"], "fill_profile": fm.name,
              "slippage_ticks": slip, "har_fit": fit, "parts": conf["parts"],
              "evidence": ev, "frozen": frozen}
    VariantCounter().record(prereg_id=conf["prereg_id"], params=params, seed=conf["seed"],
                            label="C-007 confirmation")
    v = cc.verdict(traded, seed=conf["seed"], k=conf["k"],
                   replicates=conf["bootstrap_replicates"])

    rows = [{"scope": "pooled", "statistic": k, "value": x} for k, x in v["pooled"].items()]
    for m, d in v["legs"].items():
        rows += [{"scope": m, "statistic": k, "value": x} for k, x in d.items()]
    rows += [{"scope": "leave_one_out", "statistic": k, "value": x}
             for k, x in v["leave_one_out"].items()]
    rows += [{"scope": "homogeneity", "statistic": "cochran_q", "value": v["cochran_q"]},
             {"scope": "homogeneity", "statistic": "cochran_p", "value": v["cochran_p"]}]
    rows += [{"scope": "check", "statistic": k, "value": x} for k, x in v["checks"].items()]
    rows += [{"scope": "verdict", "statistic": "best_leg", "value": v["best_leg"]},
             {"scope": "verdict", "statistic": "passes", "value": v["passes"]}]
    u = traded["u"]
    rows += [{"scope": "conduct", "statistic": "mean_win_over_mean_loss",
              "value": float(u[u > 0].mean() / -u[u < 0].mean())},
             {"scope": "pooled", "statistic": "stop_hit_rate",
              "value": float(traded["stop_hit"].mean())}]
    wide = traded.pivot_table(index="date", columns="market", values="u")
    c = wide.corr().to_numpy()
    rows.append({"scope": "pooled", "statistic": "rho_average_pairwise",
                 "value": float(c[np.triu_indices_from(c, 1)].mean())})
    for m in tx.MARKETS:
        t = alld[alld["market"] == m]
        rows.append({"scope": m, "statistic": "stop_hit_rate",
                     "value": float(t.loc[t["reason"] == "", "stop_hit"].mean())})
        rows += [{"scope": m, "statistic": f"no_trade_{r}", "value": int((t["reason"] == r).sum())}
                 for r in ("burn_in", "no_signal", "size_zero")]
        rows += [{"scope": m, "statistic": k, "value": x} for k, x in overlap[m].items()]
    note = {"prereg_id": conf["prereg_id"], "k": conf["k"],
            "costs": "assumed profile, flagged as an assumption (D-95)",
            "decision_rule": "passes = pooled criterion AND min 2 positive legs AND leave-one-out "
                             "AND homogeneity not rejected at 5 %"}
    write_result(pd.DataFrame(rows), "c007_confirmation", script="scripts/confirm_c007.py",
                 seed=conf["seed"], parameters=params, notes=note,
                 description=f"C-007 confirmation test under {conf['prereg_id']}: pooled "
                             "criterion and C-007's attached checks, confirmation window.")
    keep = ["market", "d", "c", "dir", "rvhat", "stop_ticks", "floor_bound", "contracts",
            "stop_hit", "u"]
    write_result(traded[keep], "c007_confirmation_trades", script="scripts/confirm_c007.py",
                 seed=conf["seed"], parameters=params, notes=note,
                 description=f"Every C-007 confirmation trade under {conf['prereg_id']}, with u.")
    print("PASS" if v["passes"] else "FAIL", v["checks"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
