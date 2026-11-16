"""FV1's selected configurations through D-145's campaign gate (EXPLORATORY; FV1 stays closed as a strategy).

    python scripts/campaign_fv.py NQ ES

For each market: the configuration selected by `scripts/score_fv.py` (read from `results/fv1_<market>.csv`), its
development trade log (p_ref, eligible days), e and its one-sided 95 % lower bound from the same file, then
`propedge.campaign.gate.run_gate` at the point estimate and at the lower bound, at enforcement probabilities
0 / 10 / 25 / 50 %, for one account and for the firm's cap of five (copier: the accounts share their days).

Protocol: 1.5:1 at $500 on both legs, the maximum payout as soon as eligible (`fast_take_max`, from stage one's
T5_RESULTS 2a pair), trade slots set to the log's busiest day; sizing D-117 (current tier, headroom 0.75); the
verified rules with Aeropay terms; reinvestment on. ASSUMED, pending the operator (docs/HUMAN_INPUTS.md,
"Starting bankrolls to report"): a $5,000 bankroll; a 504-trading-day horizon (the campaign default).

Writes results/fv1_<market>_campaign.csv (exploratory, development data: never a confirmation of anything).
"""
from __future__ import annotations

import argparse
import sys
import warnings
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.backtest.metrics import meets_criterion  # noqa: E402
from propedge.campaign.gate import ENFORCEMENT_LEVELS, GATE_ENFORCEMENT_P, run_gate  # noqa: E402
from propedge.campaign.payout_method import rules_for_method  # noqa: E402
from propedge.campaign.protocols import REGISTRY  # noqa: E402
from propedge.campaign.sizing import CURRENT_TIER, DEFAULT_HEADROOM_FRAC, SizingRule  # noqa: E402
from propedge.data.qc_algorithms import FV_RUNS  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402
from propedge.research import fv_score as fs  # noqa: E402

SCRIPT = "scripts/campaign_fv.py"
SEED = 20261103
BANKROLL, HORIZON, PATHS = 5_000.0, 504, 500
ACCOUNTS = (1, 5)


def campaign_market(market: str, cfg: dict, extension: bool = False, settlement: str | None = None) -> None:
    """`settlement` (D-156): None settles each trade exactly from the MAE FV1's kits export (`mae`); `legacy`
    reproduces the pre-D-156 files, which are the optimistic bound. Anything but `legacy` writes `<tag>_d156`."""
    from propedge.data.qc_algorithms import FV_EXT_RUNS

    mk = cfg["markets"][market]
    scored = read_result(ROOT / "results" / f"fv1_{market}.csv")
    sel = scored[(scored["section"] == "selection") & (scored["statistic"] == "selected")].iloc[0]
    fam, win = sel["family"], sel["window"]
    if extension:                         # the 2009-2011 selection on the 2014-2019 block (extension_1419)
        scored = read_result(ROOT / "results" / f"fv1_{market}_1419.csv")
        half, run, tag = "2014_2019", FV_EXT_RUNS[market], f"fv1_{market}_1419_campaign"
    else:
        half, run, tag = "development", FV_RUNS[market], f"fv1_{market}_campaign"
    dev = scored[(scored["section"] == "config") & (scored["family"] == fam) & (scored["window"] == win)
                 & (scored["scale"] == "p_ref") & (scored["half"] == half)].iloc[0]
    e, lb = float(dev["e"]), float(dev["lb"])
    if settlement != "legacy":
        tag += "_d156"

    days, trades = fs.split(read_result(ROOT / "results" / f"manual_{run.replace('-', '_')}.csv"))
    dev_days = days[fs.eligible(days)]["n"].tolist()
    tr = fs.configuration(trades, fam, win, "p_ref")
    blocks = fs.day_blocks(tr[tr["n"].isin(dev_days)], dev_days, tick_value=float(mk["tick_value"]))

    base = REGISTRY.get("fast_take_max")
    protocol = replace(base, name=f"fv1_{market}_{fam}_{win}", trades_per_day=max(len(b) for b in blocks),
                       family="fv1_campaign", note="FV1's development trade log through the D-145 gate")
    rules = rules_for_method("aeropay")
    sizing = SizingRule.from_ledger(CURRENT_TIER, headroom_frac=DEFAULT_HEADROOM_FRAC)
    counter = VariantCounter()
    frames = []
    for acc in ACCOUNTS:
        counter.record(prereg_id="T4:fv1:campaign", params={"model": "FV1", "market": market, "stop_family": fam,
                       "window": win, **({"block": half} if extension else {}), "protocol": base.name,
                       "accounts": acc, "bankroll": BANKROLL,
                       "horizon_days": HORIZON}, seed=SEED, exploratory=True,
                       label="D-145 campaign gate on development data, not a test")
        df, passed = run_gate(blocks, e=e, lb=lb, protocol=protocol, bankroll=BANKROLL, horizon_days=HORIZON,
                              n_paths=PATHS, seed=SEED, accounts=acc, sizing=sizing, rules=rules,
                              settlement=settlement, mode="copier")    # as run before D-157 made rotation the default
        df.insert(0, "market", market)
        df["family"], df["window"], df["e"], df["e_lb"] = fam, win, e, lb
        df["gate_passed"] = passed
        df["old_gate_met"] = meets_criterion(e, lb)
        frames.append(df)
        g = df[df["is_gate_row"]].iloc[0]
        pt = df[(df["shift"] == "point") & (df["enforcement_p"] == 0.0)].iloc[0]
        print(f"[{market}] {fam}/{win}, {acc} account(s): gate {'PASS' if passed else 'fail'} (median log growth "
              f"{g['median_log_growth']:+.3f}/yr at the lower bound, 25 % denial); at the point estimate with no "
              f"denial {pt['median_log_growth']:+.3f}/yr")
    out = pd.concat(frames, ignore_index=True)
    write_result(out, tag, script=SCRIPT, seed=SEED, exploratory=True,
                 variant_count=counter.count("T4:fv1:campaign"),
                 parameters={"evidence": [f"results/fv1_{market}.csv",
                                          f"results/manual_{run.replace('-', '_')}.csv"], "block": half,
                             "selected": f"{fam}/{win}", "e": e, "e_lb": lb, "protocol": base.name,
                             "trades_per_day": protocol.trades_per_day, "sizing": sizing.as_dict(),
                             "rules": "rules_for_method('aeropay') from the verified ledger", "mode": "copier",
                             "accounts": list(ACCOUNTS), "bankroll": BANKROLL, "horizon_days": HORIZON,
                             "paths": PATHS, "enforcement_levels": list(ENFORCEMENT_LEVELS),
                             "gate_enforcement_p": GATE_ENFORCEMENT_P,
                             "settlement": str(out["settlement"].iloc[0])},
                 notes={"decision": "D-145 (gate); FV1 D-142, closed", "status": "EXPLORATORY: development data",
                        "assumed": "bankroll $5,000 and horizon 504 trading days, pending the operator "
                                   "(docs/HUMAN_INPUTS.md); the conduct model's windows and thresholds (D-145)"},
                 description=f"FV1 on {market} ({fam}/{win}) through the D-145 campaign gate: time-aware return at "
                             "the point estimate and the lower bound of e, at four enforcement levels, for one and "
                             "five accounts, with ruin, drawdown, latency and the stacking-pattern measures.")


def main(argv: list[str] | None = None) -> int:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("markets", nargs="+", choices=sorted(FV_RUNS))
    ap.add_argument("--extension", action="store_true", help="the 2014-2019 block (R047/R048), after score_fv --extension")
    ap.add_argument("--settlement", choices=("mae", "pessimistic", "legacy"), default=None,
                    help="D-156; default: mae, from the MAE the kits export; legacy reproduces the pre-D-156 files")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load((ROOT / "config" / "model_fv.yaml").read_text(encoding="utf-8"))
    for m in a.markets:
        campaign_market(m, cfg, extension=a.extension, settlement=a.settlement)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
