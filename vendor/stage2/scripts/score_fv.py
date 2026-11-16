"""Score FV1 (D-142, config/model_fv.yaml) from the ingested cloud runs, and put the selected configuration through
the prop contract.

    python scripts/score_fv.py NQ            # R045
    python scripts/score_fv.py NQ ES         # R045 and R046
    python scripts/score_fv.py NQ ES --extension   # R047 and R048, 2014-2019 (extension_1419)

Order, declared in config/model_fv.yaml before any trade was computed:

  1. integrity: days recorded, the declared day filter (propedge/research/fv_score.py), days excluded;
  2. the four configurations (stop family x window) at both scales on the selection half, the validation half and
     the whole development window; unfiltered as a sensitivity;
  3. selection: the highest lower bound of e on the selection half at p_ref; the validation half read once for it;
  4. breakdowns of every configuration at p_ref over the development window: by year, setup, session, side;
  5. the selected configuration's full trade log;
  6. its prop simulation: $500 a trade, D-117 sizing, one Combine attempt and its funded account per path.

Writes results/fv1_<market>.csv, fv1_<market>_trades.csv and fv1_<market>_prop_paths.csv, all EXPLORATORY
(development data, written after the open-reversion results were seen). Numbers for any document come from them.
"""
from __future__ import annotations

import argparse
import sys
import warnings
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.data.qc_algorithms import FV_RUNS  # noqa: E402
from propedge.research import fv_score as fs  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

SCRIPT = "scripts/score_fv.py"
BLOCK, REPS = 20, 10_000
STATUS = ("EXPLORATORY: development data (2009-06-01 to 2014-05-27), model written after the open-reversion "
          "results were seen (D-142); never a candidate by itself (propsim D-47)")


def _audit(trades: pd.DataFrame, market: str) -> int:
    """D-148: every exported trade against FV1's declared rules; a violation is printed and recorded, never dropped."""
    from propedge.data.qc_algorithms import fv_params
    from propedge.research.trade_audit import fv1_checks, run_checks

    got = run_checks(trades, fv1_checks(fv_params(market)))
    for k, v in got.items():
        if v:
            print(f"[{market}] RULE VIOLATION: {k} ({v} trades) -- a kit or scorer defect; diagnose before use")
    return int(sum(got.values()))


def score_market(market: str, cfg: dict) -> None:
    run = FV_RUNS[market]
    evidence = ROOT / "results" / f"manual_{run.replace('-', '_')}.csv"
    mk = cfg["markets"][market]
    seed = int(cfg["measure"]["seed"])
    halves = {k: (pd.Timestamp(v[0]), pd.Timestamp(v[1])) for k, v in cfg["measure"]["halves"].items()}
    days, trades = fs.split(read_result(evidence))
    ok = fs.eligible(days)
    rows: list[dict] = []

    def add(section, **kw):
        rows.append({"market": market, "section": section, **kw})

    # ---- 1. integrity
    add("integrity", statistic="days_recorded", value=len(days))
    add("integrity", statistic="days_eligible", value=int(ok.sum()))
    add("integrity", statistic="excluded_not_settled", value=int((days["st"] != 1).sum()))
    add("integrity", statistic="excluded_no_anchor_bar", value=int(days["r0"].isna().sum()))
    add("integrity", statistic="excluded_coverage_below_90pct", value=int((days["cov"] < fs.MIN_COVERAGE).sum()))
    add("integrity", statistic="bad_bars_total", value=int(days["bad"].sum()))
    add("integrity", statistic="trades_recorded", value=len(trades))
    violations = _audit(trades, market)
    add("integrity", statistic="rule_violations", value=violations)
    print(f"[{market}] days {len(days)}, eligible {int(ok.sum())}, trades recorded {len(trades)}, "
          f"rule violations {violations}")

    elig = days[ok]
    span = {h: elig[(elig["date"] >= a) & (elig["date"] <= b)]["n"].tolist() for h, (a, b) in halves.items()}
    span["development"] = elig["n"].tolist()
    all_days = days["n"].tolist()

    # ---- 2. the four configurations
    counter = VariantCounter()
    for fam in fs.FAMILIES:
        for win in fs.WINDOWS:
            counter.record(prereg_id="T4:fv1:development", params={"model": "FV1", "market": market,
                           "stop_family": fam, "window": win}, seed=seed, exploratory=True,
                           label="development search, not a test (D-142)")
            for scale in fs.SCALES:
                tr = fs.configuration(trades, fam, win, scale)
                for half in ("selection", "validation", "development"):
                    add("config", family=fam, window=win, scale=scale, half=half,
                        **fs.summarise(tr, span[half], block=BLOCK, reps=REPS, seed=seed))
                add("config", family=fam, window=win, scale=scale, half="development_unfiltered",
                    **fs.summarise(tr, all_days, block=BLOCK, reps=REPS, seed=seed))
    conf = pd.DataFrame([r for r in rows if r["section"] == "config"])

    # ---- 3. selection, then one look at validation
    sel_rows = conf[(conf["scale"] == "p_ref") & (conf["half"] == "selection")].to_dict("records")
    chosen = fs.select(sel_rows)
    fam, win = chosen["family"], chosen["window"]
    val = conf[(conf["family"] == fam) & (conf["window"] == win) & (conf["scale"] == "p_ref")
               & (conf["half"] == "validation")].iloc[0]
    add("selection", family=fam, window=win, scale="p_ref", half="selection", statistic="selected",
        e=chosen["e"], lb=chosen["lb"], trades=chosen["trades"])
    add("selection", family=fam, window=win, scale="p_ref", half="validation", statistic="validation_look",
        e=val["e"], lb=val["lb"], trades=val["trades"])
    print(f"[{market}] selected {fam}/{win}: selection e {chosen['e']:+.3f} (LB {chosen['lb']:+.3f}), "
          f"validation e {val['e']:+.3f} (LB {val['lb']:+.3f}), {int(val['trades'])} trades")

    # ---- 4. breakdowns at p_ref over the development window
    dev = span["development"]
    dev_days = elig.set_index("n")
    for f2 in fs.FAMILIES:
        for w2 in fs.WINDOWS:
            tr = fs.configuration(trades, f2, w2, "p_ref")
            tr = tr[tr["n"].isin(dev)]
            for year, ns in dev_days.groupby(dev_days["date"].dt.year).groups.items():
                add("breakdown", family=f2, window=w2, scale="p_ref", half="development", by="year",
                    group=str(year), **fs.summarise(tr, list(ns), block=BLOCK, reps=REPS, seed=seed))
            for by, col in (("setup", "tag"), ("session", "session"), ("side", "side")):
                for g, sub in tr.groupby(col):
                    label = {1: "long", -1: "short"}.get(g, g) if by == "side" else g
                    add("breakdown", family=f2, window=w2, scale="p_ref", half="development", by=by,
                        group=str(label), **fs.summarise(sub, dev, block=BLOCK, reps=REPS, seed=seed))

    # ---- 5. the selected configuration's trade log (p_ref, development, eligible days)
    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    ps = fs.PropSettings(risk=float(cfg["prop_simulation"]["risk_per_trade"]),
                         seed=int(cfg["prop_simulation"]["seed"]))
    combine_cap = SizingRule.from_ledger(CURRENT_TIER, headroom_frac=ps.headroom_frac).cap_micros("combine", 0.0)
    sel_tr = fs.configuration(trades, fam, win, "p_ref")
    sel_tr = sel_tr[sel_tr["n"].isin(dev)]
    log = fs.trade_log(sel_tr, tick_value=float(mk["tick_value"]), risk=ps.risk, cap_micros=combine_cap)

    # ---- 6. the prop simulation
    blocks = fs.day_blocks(sel_tr, dev, tick_value=float(mk["tick_value"]))
    prop, paths = fs.prop_simulation(blocks, ps, name=f"fv1_{market}_{fam}_{win}")
    for k, v in prop.items():
        add("prop", family=fam, window=win, scale="p_ref", half="development", statistic=k,
            value=v if isinstance(v, (int, float, np.floating, np.integer)) else np.nan,
            note=None if isinstance(v, (int, float, np.floating, np.integer)) else str(v))
    print(f"[{market}] prop: P(pass) {prop['p_pass']:.3f}, P(fail) {prop['p_fail']:.3f}, median days to pass "
          f"{prop['median_days_to_pass']}, P(any payout) {prop['p_any_payout']:.3f}, mean net cash "
          f"{prop['mean_net_cash']:,.0f}")

    n_var = counter.count("T4:fv1:development")
    common = dict(script=SCRIPT, seed=seed, exploratory=True, prereg_id=None, variant_count=n_var,
                  notes={"decision": "D-142 (declared before any trade was computed)", "status": STATUS,
                         "day_filter": fs.__doc__.split("Day filter")[1].split("\n\n")[0].strip(),
                         "selected": f"{fam}/{win}"})
    params = {"evidence": str(evidence.relative_to(ROOT)), "design": "config/model_fv.yaml", "market": market,
              "block_days": BLOCK, "replicates": REPS, "halves": {k: [str(a.date()), str(b.date())]
                                                                  for k, (a, b) in halves.items()},
              "prop": asdict(ps), "combine_cap_micros": combine_cap}
    write_result(pd.DataFrame(rows), f"fv1_{market}", parameters=params,
                 description=f"FV1 on {market}: integrity, the four configurations at both scales by half, the "
                             "selection and its one validation look, breakdowns, and the prop simulation.", **common)
    write_result(log, f"fv1_{market}_trades", parameters=params,
                 description=f"FV1 on {market}: every trade of the selected configuration ({fam}/{win}, p_ref) "
                             "over the development window, with a Combine account's contracts and dollars.",
                 **common)
    write_result(paths, f"fv1_{market}_prop_paths", parameters={**params, "prop_seed": ps.seed},
                 description=f"FV1 on {market}: one row per simulated Combine attempt and its funded account.",
                 **{**common, "seed": ps.seed})


def score_extension(market: str, cfg: dict) -> None:
    """config/model_fv.yaml `extension_1419`: FV1 unchanged on 2014-05-28 to 2019-12-31. Nothing is selected here;
    every configuration is reported and the one selected on 2009-2011 is read once."""
    from propedge.data.qc_algorithms import FV_EXT_RUNS

    ext = cfg["extension_1419"]
    run = FV_EXT_RUNS[market]
    evidence = ROOT / "results" / f"manual_{run.replace('-', '_')}.csv"
    seed = int(ext["seed"])
    days, trades = fs.split(read_result(evidence))
    ok = fs.eligible(days)
    block = days[ok]["n"].tolist()
    prior = read_result(ROOT / "results" / f"fv1_{market}.csv")
    sel = prior[(prior["section"] == "selection") & (prior["statistic"] == "selected")].iloc[0]
    rows: list[dict] = []

    def add(section, **kw):
        rows.append({"market": market, "section": section, **kw})

    add("integrity", statistic="days_recorded", value=len(days))
    add("integrity", statistic="days_eligible", value=int(ok.sum()))
    add("integrity", statistic="bad_bars_total", value=int(days["bad"].sum()))
    add("integrity", statistic="trades_recorded", value=len(trades))
    add("integrity", statistic="rule_violations", value=_audit(trades, market))
    elig = days[ok].set_index("n")
    for fam in fs.FAMILIES:
        for win in fs.WINDOWS:
            for scale in fs.SCALES:
                tr = fs.configuration(trades, fam, win, scale)
                chosen = fam == sel["family"] and win == sel["window"]
                add("config", family=fam, window=win, scale=scale, half="2014_2019", selected_on_2009_2011=chosen,
                    **fs.summarise(tr, block, block=BLOCK, reps=REPS, seed=seed))
                add("config", family=fam, window=win, scale=scale, half="2014_2019_unfiltered",
                    selected_on_2009_2011=chosen,
                    **fs.summarise(tr, days["n"].tolist(), block=BLOCK, reps=REPS, seed=seed))
                if scale == "p_ref":
                    for year, ns in elig.groupby(elig["date"].dt.year).groups.items():
                        add("breakdown", family=fam, window=win, scale=scale, half="2014_2019", by="year",
                            group=str(year), **fs.summarise(tr, list(ns), block=BLOCK, reps=REPS, seed=seed))
    got = [r for r in rows if r["section"] == "config" and r.get("selected_on_2009_2011") and r["scale"] == "p_ref"
           and r["half"] == "2014_2019"][0]
    print(f"[{market}] 2014-2019, {len(block)} eligible days; the 2009-2011 selection {sel['family']}/{sel['window']}: "
          f"e {got['e']:+.3f} (LB {got['lb']:+.3f}) on {got['trades']} trades")

    from propedge.campaign.sizing import CURRENT_TIER, SizingRule

    ps = fs.PropSettings(risk=float(cfg["prop_simulation"]["risk_per_trade"]), seed=seed)
    cap = SizingRule.from_ledger(CURRENT_TIER, headroom_frac=ps.headroom_frac).cap_micros("combine", 0.0)
    tr = fs.configuration(trades, sel["family"], sel["window"], "p_ref")
    log = fs.trade_log(tr[tr["n"].isin(block)], tick_value=float(cfg["markets"][market]["tick_value"]), risk=ps.risk,
                       cap_micros=cap)
    common = dict(script=SCRIPT, seed=seed, exploratory=True, prereg_id=None,
                  notes={"decision": "D-142 model, D-144 block, declared in config/model_fv.yaml extension_1419",
                         "status": "EXPLORATORY: development data 2014-05-28 to 2019-12-31; nothing selected on it"})
    params = {"evidence": str(evidence.relative_to(ROOT)), "design": "config/model_fv.yaml extension_1419",
              "market": market, "block_days": BLOCK, "replicates": REPS,
              "selected_on_2009_2011": f"{sel['family']}/{sel['window']}"}
    write_result(pd.DataFrame(rows), f"fv1_{market}_1419", parameters=params,
                 description=f"FV1 unchanged on {market}, 2014-2019: every configuration at both scales, by year, and "
                             "the 2009-2011 selection read once.", **common)
    write_result(log, f"fv1_{market}_1419_trades", parameters=params,
                 description=f"FV1 on {market}, 2014-2019: every trade of the configuration selected on 2009-2011 "
                             "(p_ref), with a Combine account's contracts and dollars.", **common)


def main(argv: list[str] | None = None) -> int:
    warnings.filterwarnings("ignore")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("markets", nargs="+", choices=sorted(FV_RUNS))
    ap.add_argument("--extension", action="store_true",
                    help="score R047/R048, the 2014-2019 block (config/model_fv.yaml extension_1419)")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load((ROOT / "config" / "model_fv.yaml").read_text(encoding="utf-8"))
    for m in a.markets:
        (score_extension if a.extension else score_market)(m, cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
