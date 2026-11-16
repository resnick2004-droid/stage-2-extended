"""EXPLORATORY: IM2's development entries as a Studio trade log, so the Campaign Studio (Stage 2C) can replay the
verdict's campaigns for inspection (the operator, 2026-10-01; the research protocol: the Studio is step 7's inspection
view, never a verdict).

    python scripts/im2_trades_export.py

From the verdict's entry table and day set (`breakeven_report.development_table`: R053-R060, D-209's fees), one row per
entry with a walk at the reference-price scale `p` (D-106), the verdict's primary scale, in the order the verdict's day
blocks hold them (`im2_score.blocks`: entry time, ties ES, CL, 6E, NG). Writes results/im2_development_trades.csv in
the Studio's canonical schema plus the per-R columns the engine's policy reads (`DayBlock.r_by_rr` / `mae_by_rr`):

* `timestamp_in`, `timestamp_out`: the entry bar's start and the 2:1 exit bar's end -- the times the verdict's run used
  for flat routing (D-159) -- as ISO times with their America/Chicago offset; every exit is at or before 15:10 CT.
* `symbol` the micro, `side` long/short, `contracts` 1.
* **Prices are constructed for the Studio's single-R views, not quoted**: `entry_price` is the decision bar's actual
  close; `stop`, `target` (2R) and `exit_price` sit at the reference-scale distance from it, so |entry - stop| x the
  micro's point value is the verdict's risk per micro (`rpc_p`) exactly. They may fall off the tick grid.
* At R = 2, the primary R (the build leg): `exit_reason` (target, stop -- a gap through it included -- or flatten),
  `pnl_gross` and `pnl_net` in dollars for one micro (`r2_p` and `v2_p` x the risk), `mae` in dollars (the same
  `max(mae2_p, -r2_p)` the verdict's blocks carry, x the risk).
* `dollars_risked` = `rpc_p`; `r_net_1`, `r_net_2` = `v1_p`, `v2_p`, and `mae_r_1`, `mae_r_2` = max(`mae{R}_p`,
  -`r{R}_p`): exactly the values the verdict's run read as `r_by_rr` and `mae_by_rr`.

The manifest carries the run the Studio should mirror (`parameters.mirror`): the gate's unshifted arm, the one whose
paths can reproduce (the Studio replays unshifted outcomes). It reads no new data and selects nothing: the verdict's
own outcomes, re-presented.

Beside it, results/im2_development_dayset.csv: the verdict's day set, one row per date with its entry count. The
campaign draws one block per day of the day set, **days without an entry included** (`im2_score.blocks`); a replay
that sees only the log's trade days draws a trade on more of its days than the verdict did.
"""
from __future__ import annotations

import sys
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.reporting.pin import engine_pin  # noqa: E402
from propedge.reporting.results import write_result  # noqa: E402
from propedge.research import im2_score as sc  # noqa: E402

SCRIPT = "scripts/im2_trades_export.py"
CT = ZoneInfo("America/Chicago")
SCALE = "p"
KIND = {"t": "target", "s": "stop", "g": "stop", "m": "flatten"}


def _stamp(d: str, minutes: float) -> str:
    base = datetime(int(d[:4]), int(d[4:6]), int(d[6:8]), tzinfo=CT)
    return (base + timedelta(minutes=float(minutes))).isoformat()


def trade_log(table: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """The Studio log from the verdict's entry table (see the module docstring)."""
    specs = sc.micro_specs(cfg)
    order = {m: i for i, m in enumerate(sc.MARKETS)}
    x = table[table[f"dist_{SCALE}"].notna()].copy()
    x["_o"] = x["market"].map(order)
    x = x.sort_values(["d", "entry_t", "_o"], kind="stable").reset_index(drop=True)
    if (x[f"exit_t_{SCALE}"] > 15 * 60 + 10).any():
        raise ValueError("an exit after 15:10 CT: the Studio's loader refuses it (Topstep 8284206)")
    pv = x["market"].map({m: specs[m]["point_value"] for m in sc.MARKETS})
    dist = x[f"dist_{SCALE}"]
    side = np.where(x["side"] > 0, 1.0, -1.0)
    entry = x["cl"]
    risk = x[f"rpc_{SCALE}"]
    mae_r = {R: np.maximum(x[f"mae{R}_{SCALE}"], -x[f"r{R}_{SCALE}"]) for R in (1, 2)}
    return pd.DataFrame({
        "timestamp_in": [_stamp(d, m) for d, m in zip(x["d"], x["entry_t"])],
        "timestamp_out": [_stamp(d, m) for d, m in zip(x["d"], x[f"exit_t_{SCALE}"])],
        "symbol": x["market"].map({m: cfg["markets"][m]["micro"] for m in sc.MARKETS}),
        "side": np.where(side > 0, "long", "short"),
        "entry_price": entry,
        "stop": entry - side * dist,
        "target": entry + side * 2.0 * dist,
        "exit_price": entry + side * x[f"r2_{SCALE}"] * dist,
        "contracts": 1,
        "pnl_gross": x[f"r2_{SCALE}"] * risk,
        "pnl_net": x[f"v2_{SCALE}"] * risk,
        "exit_reason": x[f"kind2_{SCALE}"].map(KIND).fillna("other"),
        "dollars_risked": risk,
        "mae": mae_r[2] * risk,
        "r_net_1": x[f"v1_{SCALE}"],
        "r_net_2": x[f"v2_{SCALE}"],
        "mae_r_1": mae_r[1],
        "mae_r_2": mae_r[2],
    }).assign(_check=(dist * pv - risk).abs()).pipe(_checked)


def _checked(df: pd.DataFrame) -> pd.DataFrame:
    if (df["_check"] > 1e-6).any():
        raise ValueError("|entry - stop| x point value does not reproduce the verdict's risk per micro")
    if (df[["mae", "mae_r_1", "mae_r_2"]] < -1e-12).any().any():
        raise ValueError("a negative MAE")
    return df.drop(columns="_check")


def mirror() -> dict:
    """The gate's unshifted arm as the verdict ran it (`im2_score.run_gate` -> `propedge.campaign.gate.run_gate`)."""
    from propedge.campaign.gate import GATE_ENFORCEMENT_P
    from propedge.campaign.sizing import CURRENT_TIER, DEFAULT_HEADROOM_FRAC

    p = sc.protocol(1)
    return {
        "shift": "point (unshifted; the lower-bound arm shifts each R by its bound less e and will not reproduce)",
        "mode": "rotation", "flat_routing": True, "markets": list(sc.MARKETS),
        "sizing": f"SizingRule.from_ledger({CURRENT_TIER!r}, headroom_frac={DEFAULT_HEADROOM_FRAC}): tier sizing in "
                  "whole micros, the state's risk over the risk per contract, floored, capped by the tier allowance",
        "accounts": sc.ACCOUNTS, "combines": sc.ACCOUNTS, "total_accounts": sc.ACCOUNTS,
        "horizon_days": sc.HORIZON, "n_paths": sc.PATHS, "seed": sc.SEED, "settlement": "mae",
        "enforcement_p_levels": [0.0, 0.10, 0.25, 0.50], "gate_enforcement_p": GATE_ENFORCEMENT_P,
        "conduct": "ConductModel(enforcement_p=level), Responsible Trading Program on",
        "payout_method": "aeropay", "rules": "rules_for_method('aeropay')", "bankroll": sc.BANKROLL,
        "protocol": {"name": p.name, "combine_rr": p.combine_rr, "combine_risk": p.combine_risk,
                     "funded_rr": p.funded_rr, "funded_risk": p.funded_risk,
                     "trades_per_day": "the busiest day's entry count (im2_score.protocol(busiest)); the policy's "
                                       "max_trades caps each state",
                     "payout_path": p.payout_path, "keep_balance": p.keep_balance, "payout_frac": p.payout_frac,
                     "max_concurrent_accounts": p.max_concurrent_accounts},
        "risk_policy": sc.policy().as_dict(),
        "verdict_rows": "results/im2_development_gate.csv, outcome v, scale p, shift point",
    }


def main(results_dir: Path | None = None) -> int:
    from breakeven_report import development_table

    warnings.filterwarnings("ignore")
    cfg = sc.config()
    rt = sc.fees(cfg)
    table, days = development_table(cfg, rt)
    log = trade_log(table, cfg)
    busiest = int(table[table[f"dist_{SCALE}"].notna()].groupby("d").size().max())
    m = mirror()
    m["protocol"]["trades_per_day"] = busiest
    write_result(log, "im2_development_trades", script=SCRIPT, seed=sc.SEED, exploratory=True,
                 results_dir=results_dir, provenance={"engine": engine_pin()},
                 parameters={"scale": SCALE, "primary_r": 2, "round_turn": rt, "days": len(days), "mirror": m,
                             "prices": "constructed: entry at the decision bar's actual close, stop, target and exit "
                                       "at the reference-scale distance (|entry - stop| x point value = rpc_p)"},
                 notes={"status": "EXPLORATORY: the verdict's own outcomes re-presented for the Studio (D-210)"},
                 description="EXPLORATORY: IM2's development entries at the reference-price scale as a Studio trade "
                             "log -- canonical columns at R = 2 plus r_net_1, r_net_2, mae_r_1, mae_r_2 exactly as the "
                             "verdict's run read them -- and, in the manifest, the gate arm a replay should mirror.")
    counts = table[table[f"dist_{SCALE}"].notna()].groupby("d").size()
    dayset = pd.DataFrame({"date": [f"{d[:4]}-{d[4:6]}-{d[6:]}" for d in days],
                           "entries": [int(counts.get(d, 0)) for d in days]})
    write_result(dayset, "im2_development_dayset", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir, provenance={"engine": engine_pin()},
                 parameters={"scale": SCALE, "period": list(sc.DEVELOPMENT),
                             "rule": "every date at least one market's calendar schedules as a full session (P-04 §4)"},
                 notes={"status": "EXPLORATORY: the verdict's day set, for a replay to draw its empty days too"},
                 description="EXPLORATORY: IM2's development day set, one row per date with its entry count at the "
                             "reference scale; the verdict's campaign draws one block per date, empty ones included.")
    print(f"{len(log)} entries written; busiest day {busiest}; {len(days)} days, {int((dayset['entries'] == 0).sum())} "
          f"without an entry; mirror: seed {m['seed']}, {m['n_paths']} paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
