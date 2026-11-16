"""One scorecard for every model tested, for the Studio and the reports to read in one place (D-148's companion).

    python scripts/model_scorecard.py

Writes results/model_scorecard.csv: one row per (model, market, period, configuration), ids as plain strings. Every
number is read from the model's own result files (named in `source`); nothing is recomputed here except the
pessimistic win rate, defined below. Paths are relative to the Stage 2 root.

Columns: trades, trades_per_day, win_rate, avg_win_r, avg_loss_r, e, e_lb; `pessimistic_win_rate`, the win rate
that gives e's one-sided 95 % lower bound at this configuration's own average win and loss sizes,
(e_lb + |avg_loss_r|) / (avg_win_r + |avg_loss_r|); `old_gate_met` (propsim D-47: e >= 0.10 and e_lb >= 0.05); the
D-145 campaign gate where it was run (`gate_verdict`, and median log growth per year at the point estimate and at
the lower bound, 25 % denial, for one and five accounts); `rule_violations` from the trade audit; and the paths of
the trade log, the run file, the audit and the chart-review sheet.

A new model adds a builder below; the file is regenerated whole.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.backtest.metrics import meets_criterion  # noqa: E402
from propedge.data.qc_algorithms import FV_EXT_RUNS, FV_RUNS  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

RESULTS = ROOT / "results"
GATE_P = 0.25


def _rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix() if p.exists() else ""


def _pessimistic(row) -> float:
    w, l = float(row["avg_win_r"]), abs(float(row["avg_loss_r"]))
    return float((row["lb"] + l) / (w + l)) if np.isfinite(w + l) and w + l > 0 else float("nan")


def _gate(campaign: Path) -> dict:
    """The D-145 gate columns from a campaign file, or blanks when the gate was not run."""
    if not campaign.exists():
        return {"gate_verdict": "not run"}
    c = read_result(campaign)
    out = {"gate_verdict": "pass" if bool(c["gate_passed"].any()) else "fail", "campaign_file": _rel(campaign)}
    for acc in sorted(c["accounts"].unique()):
        for shift, key in (("point", "point"), ("lower_bound", "lb")):
            r = c[(c["accounts"] == acc) & (c["shift"] == shift) & (c["enforcement_p"] == GATE_P)]
            out[f"growth_{key}_{int(acc)}acct"] = float(r["median_log_growth"].iloc[0]) if len(r) else float("nan")
    return out


def fv1_rows() -> list[dict]:
    audit = read_result(RESULTS / "trade_audit_fv1.csv")
    violations = audit.groupby("run")["violations"].sum().to_dict()
    # (file, half label in it, period id, run map, selected-config trade log, campaign file); the campaign files are
    # D-156's, settled from each trade's MAE (the pre-D-156 files are kept on record, not read here)
    blocks = [
        ("fv1_{m}.csv", "selection", "2009-2011", FV_RUNS, None, None),
        ("fv1_{m}.csv", "validation", "2012-2014", FV_RUNS, None, None),
        ("fv1_{m}.csv", "development", "2009-2014", FV_RUNS, "fv1_{m}_trades.csv", "fv1_{m}_campaign_d156.csv"),
        ("fv1_{m}_1419.csv", "2014_2019", "2014-2019", FV_EXT_RUNS, "fv1_{m}_1419_trades.csv",
         "fv1_{m}_1419_campaign_d156.csv"),
    ]
    rows = []
    for market in ("NQ", "ES"):
        scored = read_result(RESULTS / f"fv1_{market}.csv")
        sel = scored[(scored["section"] == "selection") & (scored["statistic"] == "selected")].iloc[0]
        review = ROOT / "docs" / "reviews" / f"FV1_{market}_review.md"
        for fname, half, period, runs, log, camp in blocks:
            src = RESULTS / fname.format(m=market)
            r = read_result(src)
            run = runs[market]
            run_file = RESULTS / f"manual_{run.replace('-', '_')}.csv"
            for _, c in r[(r["section"] == "config") & (r["half"] == half)].iterrows():
                selected = c["family"] == sel["family"] and c["window"] == sel["window"] and c["scale"] == "p_ref"
                row = {
                    "model": "FV1", "market": market, "period": period,
                    "configuration": f"{c['family']}/{c['window']}/{c['scale']}",
                    "selected_on_2009_2011": bool(c["family"] == sel["family"] and c["window"] == sel["window"]),
                    "trades": int(c["trades"]), "trades_per_day": float(c["trades_per_day"]),
                    "win_rate": float(c["win_rate"]), "avg_win_r": float(c["avg_win_r"]),
                    "avg_loss_r": float(c["avg_loss_r"]), "e": float(c["e"]), "e_lb": float(c["lb"]),
                    "pessimistic_win_rate": _pessimistic(c), "old_gate_met": meets_criterion(c["e"], c["lb"]),
                    "rule_violations": int(violations.get(run, -1)),
                    "trade_log": _rel(RESULTS / log.format(m=market)) if (log and selected) else "",
                    "run_file": _rel(run_file), "audit_file": _rel(RESULTS / "trade_audit_fv1.csv"),
                    "review_sheet": _rel(review) if period == "2014-2019" and selected else "",
                    "source": _rel(src), "status": "exploratory, development data",
                }
                row.update(_gate(RESULTS / camp.format(m=market)) if (camp and selected) else {"gate_verdict": "not run"})
                rows.append(row)
    return rows


BUILDERS = {"FV1": fv1_rows}


def main() -> int:
    rows = [r for build in BUILDERS.values() for r in build()]
    out = pd.DataFrame(rows)
    for col in ("model", "market", "period", "configuration"):
        out[col] = out[col].astype(str)
    write_result(out, "model_scorecard", script="scripts/model_scorecard.py", seed=None, require_seed=False,
                 parameters={"models": sorted(BUILDERS), "gate_enforcement_p": GATE_P,
                             "pessimistic_win_rate": "(e_lb + |avg_loss_r|) / (avg_win_r + |avg_loss_r|)"},
                 notes={"reads": "each model's own result files, named per row in `source`",
                        "for": "Stage 2C's Studio and the reports: one row per (model, market, period, configuration)"},
                 description="Every model tested: win rate, pessimistic win rate, edge and its bound, the D-145 "
                             "gate where run, the rule audit, and where each row's trade log and sources are.")
    print(f"{len(out)} rows")
    pd.set_option("display.width", 220)
    sel = out[out["gate_verdict"] != "not run"]
    print(sel[["model", "market", "period", "configuration", "trades", "win_rate", "pessimistic_win_rate", "e",
               "e_lb", "gate_verdict", "growth_point_1acct", "growth_lb_1acct", "trade_log"]].round(3).to_string(
        index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
