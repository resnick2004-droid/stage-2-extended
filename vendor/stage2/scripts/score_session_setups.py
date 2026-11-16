"""EXPLORATORY (T15 item 8; D-245): score the session-setup screen SS1 -- which setups, at which times of day, carry a
net edge per trade on NQ and ES -- by rules fixed in config/session_setups.yaml before any count was read.

    python scripts/score_session_setups.py

Reads the ingested runs R097 (NQ) and R098 (ES) (`results/manual_R09x_setups_<market>.csv`, `propedge/data/
setup_parser.py`'s table). A **variant** is a market, window, rule, stop multiple and R, both directions together (the
rule decides the direction); k, their number, is reported with every reading (D-189).

* **Each variant's edge per trade**, in R, over a period: a target pays R, a stop costs 1, a bracket open at the 15:10
  flatten counts as a full loss, less D-238's cost (D-221's round turn and slippage, the entry minute's measured spread
  beyond the tick the walk charged, the measured overshoot on each stop exit) over the stop's dollars per micro, through
  the mean of 1 / stop (`regime_then_now.cost_per_micro`). Pooled for the point; per calendar year for the bound --
  the yearly estimates' mean less the one-sided 95 % t quantile with years - 1 degrees of freedom times their standard
  error.
* **Selection (2009-2019)** -- on the GROSS edge, before costs (D-246): a variant is ranked if it resolves at its target
  or stop on at least 98 % of its trades overall and in every year (D-212) and has at least `min_trades` trades; the
  `shortlist` best distinct setups by the lower bound of their yearly gross edge, if above zero and above the no-skill
  baseline's gross edge, go to validation. Costs in R were several times larger when the stops were a few points
  (2009-2013), so ranking on the net edge there would discard setups whose skill is real and whose costs today are
  small; the check below charges today's costs in full.
* **Validation (2020-2025)**, never chosen on: a shortlisted variant survives if its net edge and its lower bound there
  -- one-sided at `validation_alpha`, 0.05 over the shortlist (D-246) -- are both above zero and it resolves as above in
  every year.
* **The no-skill baseline (D-246)**: in both periods a survivor's net edge must exceed that of the regime map's
  random-direction entries (R090, R091; D-238) at the same window -- its decision slots from the window's start to the
  end of its span -- the same trailing-range stop and R, net of the same cost (`baseline`).

Writes results/session_setups_score.csv: `variant` rows (every variant, both periods, its flags), `direction` rows
(each shortlisted variant's long and short trades apart, a diagnostic), `window` rows (per market and window: the
variants ranked and the best selection bound with its validation reading) and one `summary` row. A survivor is not a
result: it becomes a model card (D-155) and must pass one registered confirmation on the held-back year.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

SCRIPT = "scripts/score_session_setups.py"
KEY = ["market", "window", "rule", "stop_index", "R"]


def load_counts(results_dir: Path) -> tuple[pd.DataFrame, list[str]]:
    from propedge.data.setup_kit import SETUP_RUNS

    frames, have = [], []
    for market, run_id in SETUP_RUNS.items():
        f = results_dir / f"manual_{run_id.replace('-', '_')}.csv"
        if f.exists():
            frames.append(pd.read_csv(f, low_memory=False))
            have.append(market)
    return (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()), have


def reading(g: pd.DataFrame, ev: pd.DataFrame, R: float, q: dict, fee: float, slip: dict) -> dict:
    """One set of count rows at R (`ev`: the same cells at the largest R, whose stop count is the stop exits the gaps
    were measured on): trades, shares, cost and net edge."""
    from regime_then_now import cost_per_micro

    tick_dollars = q["micro_tick"] * q["micro_point_value"]
    n, t, s, o = (int(g[k].sum()) for k in ("n", "target", "stop", "open"))
    if not n:
        return {"n": 0}
    quotes = float(g["quotes"].sum())
    spread = float(g["spread_ticks_sum"].sum()) / quotes if quotes else float("nan")
    exits = int(ev["stop"].sum())
    over = float(ev["overshoot_ticks_sum"].sum()) / exits if exits else 0.0
    inv = float(g["inv_stop_sum"].sum()) / n
    cost = cost_per_micro(fee, tick_dollars, spread, s / n, o / n, over, slip)
    gross = (t * R - s - o) / n
    return {"n": n, "target_share": t / n, "stop_share": s / n, "open_share": o / n, "resolved_share": (t + s) / n,
            "spread_ticks_mean": spread, "overshoot_ticks_per_exit": over, "stop_ticks_mean": n / inv if inv else
            float("nan"), "e_gross": gross, "cost_r": cost * inv / tick_dollars, "e_net": gross - cost * inv /
            tick_dollars}


def period(g: pd.DataFrame, ev: pd.DataFrame, R: float, years: tuple[int, int], q: dict, fee: float,
           slip: dict, alpha: float = 0.05) -> dict:
    """A variant over a period: the pooled reading, each year's net edge and resolution, and the one-sided lower
    bound at `alpha`."""
    from scipy import stats

    a, b = years
    gp, ep = g[g["year"].between(a, b)], ev[ev["year"].between(a, b)]
    out = reading(gp, ep, R, q, fee, slip)
    if not out["n"]:
        return out
    ys = []
    for y, gy in gp.groupby("year"):
        r = reading(gy, ep[ep["year"] == y], R, q, fee, slip)
        if r["n"]:
            ys.append((int(y), r["e_net"], r["resolved_share"], r["e_gross"]))
    tq = stats.t.ppf(1.0 - alpha, len(ys) - 1) if len(ys) > 1 else float("nan")

    def bound(i):
        e = pd.Series([x[i] for x in ys], dtype=float)
        return float(e.mean() - tq * e.std(ddof=1) / math.sqrt(len(e))) if len(e) > 1 else float("nan")

    out.update({"years": len(ys), "e_net_lower_bound": bound(1), "e_gross_lower_bound": bound(3),
                "worst_year_resolved": min(x[2] for x in ys), "worst_year_e_net": min(x[1] for x in ys)})
    return out


def baseline(regime: pd.DataFrame, market: str, start: int, span: int, multiple: float, R: float,
             years: tuple[int, int], q: dict, fee: float, slip: dict, gross: bool = False) -> float:
    """D-246: the no-skill baseline -- the regime map's random-direction entries at the window's decision slots
    [start, start + span), at the same trailing-range stop multiple and R, both directions, net of D-238's cost; NaN
    without counts."""
    from regime_then_now import cost_per_micro

    if regime is None or regime.empty:
        return float("nan")
    a, b = years
    r = regime[(regime["market"] == market) & regime["year"].between(a, b)
               & regime["decision_slot"].between(start, start + span - 1)]
    c = r[(r["kind"] == "count") & (r["stop_kind"] == "range") & (r["stop_value"].astype(float) == float(multiple))]
    g, ev = c[c["R"] == R], c[c["R"] == max(q["rr"])]
    n, t, s, o = (int(g[k].sum()) for k in ("n", "target", "stop", "open"))
    if not n:
        return float("nan")
    sp = r[r["kind"] == "spread"]
    qn = float(sp["spread_count"].sum())
    spread = float((sp["spread_ticks_mean"].astype(float) * sp["spread_count"].astype(float)).sum()) / qn if qn else \
        float("nan")
    exits = int(ev["stop"].sum())
    over = float(ev["overshoot_ticks_sum"].sum()) / exits if exits else 0.0
    inv = float(g["inv_stop_sum"].sum()) / n
    tick_dollars = q["micro_tick"] * q["micro_point_value"]
    cost = cost_per_micro(fee, tick_dollars, spread, s / n, o / n, over, slip)
    return (t * R - s - o) / n - (0.0 if gross else cost * inv / tick_dollars)


def load_baseline(results_dir: Path, cfg: dict) -> pd.DataFrame:
    """The regime map's counts the baseline reads (D-246), or an empty frame."""
    frames = []
    for market, run in cfg["screen"].get("baseline_runs", {}).items():
        f = results_dir / f"manual_{run.replace('-', '_')}.csv"
        if f.exists():
            frames.append(pd.read_csv(f, low_memory=False))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def score(counts: pd.DataFrame, cfg: dict, fees: dict, slip: dict, regime: pd.DataFrame | None = None) -> pd.DataFrame:
    from propedge.data.setup_kit import params

    sc = cfg["screen"]
    alpha = float(sc.get("validation_alpha", 0.05))
    sel_y, val_y = tuple(sc["selection_years"]), tuple(sc["validation_years"])
    floor = float(sc["resolved_share_min"])
    c = counts[counts["kind"] == "count"]
    rows = []
    for market, cm in c.groupby("market"):
        q = params(market, cfg)
        fee, r_max = float(fees[q["micro"]]), max(q["rr"])
        starts = dict(zip(q["window_names"], q["windows"]))
        for (window, rule, si), gv in cm.groupby(["window", "rule", "stop_index"]):
            ev = gv[gv["R"] == r_max]
            start, span = starts[window]
            for R, g in gv.groupby("R"):
                row = {"section": "variant", "market": market, "window": window,
                       "window_start_ct": g["window_start_ct"].iloc[0], "rule": rule, "stop_index": int(si),
                       "stop_multiple": float(g["stop_multiple"].iloc[0]), "R": float(R)}
                for name, yrs, al in (("sel", sel_y, 0.05), ("val", val_y, alpha)):
                    for k, v in period(g, ev, float(R), yrs, q, fee, slip, al).items():
                        row[f"{name}_{k}"] = v
                    row[f"{name}_baseline_e_net"] = baseline(regime, market, start, span, row["stop_multiple"],
                                                             float(R), yrs, q, fee, slip)
                    row[f"{name}_baseline_e_gross"] = baseline(regime, market, start, span, row["stop_multiple"],
                                                               float(R), yrs, q, fee, slip, gross=True)
                n_sel = row.get("sel_n", 0) or 0
                row["eligible"] = bool(n_sel >= int(sc["min_trades"]) and row.get("sel_resolved_share", 0) >= floor
                                       and row.get("sel_worst_year_resolved", 0) >= floor)
                rows.append(row)
    out = pd.DataFrame(rows)
    out["shortlisted"] = False
    # D-246: ranked on the gross edge's bound in 2009-2019 -- skill, not that era's cost scale
    elig = out[out["eligible"] & (out["sel_e_gross_lower_bound"] > 0)].sort_values("sel_e_gross_lower_bound",
                                                                                    ascending=False)
    # one per setup (market, window, rule) -- its stops and R are the same trades -- at its best stop and R (the
    # pre-run review's S2), the best setups by that bound
    distinct = elig.drop_duplicates(["market", "window", "rule"])
    out.loc[distinct.index[: int(sc["shortlist"])], "shortlisted"] = True
    beats = (out["sel_e_gross"] > out["sel_baseline_e_gross"]) & (out["val_e_net"] > out["val_baseline_e_net"])
    out["beats_baseline"] = beats                              # D-246; a NaN baseline beats nothing
    out["survives"] = out["shortlisted"] & (out["val_e_net"] > 0) & (out["val_e_net_lower_bound"] > 0) & (
        out["val_resolved_share"] >= floor) & (out["val_worst_year_resolved"] >= floor) & beats
    return out


def directions(counts: pd.DataFrame, variants: pd.DataFrame, cfg: dict, fees: dict, slip: dict) -> pd.DataFrame:
    """Each shortlisted variant's long and short trades apart, in both periods (a diagnostic, never a selection)."""
    from propedge.data.setup_kit import params

    sc = cfg["screen"]
    c = counts[counts["kind"] == "count"]
    rows = []
    for _, v in variants[variants["shortlisted"]].iterrows():
        q = params(v["market"], cfg)
        fee, r_max = float(fees[q["micro"]]), max(q["rr"])
        g = c[(c["market"] == v["market"]) & (c["window"] == v["window"]) & (c["rule"] == v["rule"])
              & (c["stop_index"] == v["stop_index"])]
        for d, gd in g.groupby("direction"):
            row = {"section": "direction", **{k: v[k] for k in KEY}, "direction": d}
            for name, yrs in (("sel", tuple(sc["selection_years"])), ("val", tuple(sc["validation_years"]))):
                r = period(gd[gd["R"] == v["R"]], gd[gd["R"] == r_max], float(v["R"]), yrs, q, fee, slip)
                row.update({f"{name}_n": r["n"], f"{name}_e_net": r.get("e_net", float("nan"))})
            rows.append(row)
    return pd.DataFrame(rows)


def windows(variants: pd.DataFrame) -> pd.DataFrame:
    """Per market and window: variants, ranked, with a positive selection bound, and the best by it with its
    validation reading -- the AM hypothesis read against the rest of the day."""
    rows = []
    for (market, window), g in variants.groupby(["market", "window"]):
        e = g[g["eligible"]]
        best = e.sort_values("sel_e_gross_lower_bound", ascending=False).head(1)
        b = best.iloc[0] if len(best) else None
        rows.append({"section": "window", "market": market, "window": window,
                     "window_start_ct": g["window_start_ct"].iloc[0], "variants": len(g), "eligible": len(e),
                     "positive_selection_bound": int((e["sel_e_gross_lower_bound"] > 0).sum()),
                     "median_sel_e_gross": float(e["sel_e_gross"].median()) if len(e) else float("nan"),
                     "median_val_e_net": float(e["val_e_net"].median()) if len(e) else float("nan"),
                     "best_rule": b["rule"] if b is not None else "", "best_stop_multiple":
                     b["stop_multiple"] if b is not None else float("nan"), "best_R": b["R"] if b is not None else
                     float("nan"), "best_sel_e_gross_lower_bound": b["sel_e_gross_lower_bound"] if b is not None
                     else float("nan"), "best_val_e_net": b["val_e_net"] if b is not None else float("nan"),
                     "best_val_e_net_lower_bound": b["val_e_net_lower_bound"] if b is not None else float("nan")})
    return pd.DataFrame(rows)


def grid_k(cfg: dict) -> int:
    """D-189's k: the declared grid, markets x windows x rules x stops x R -- not the variants that happen to hold
    trades."""
    return (len(cfg["markets"]) * len(cfg["windows"]) * len(cfg["rules"]) * len(cfg["stops_range"]["multiples"])
            * len(cfg["rr"]))


def main(results_dir: Path | None = None, record: bool = True) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.data.setup_kit import MARKETS, SETUP_RUNS, config
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import write_result

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    counts, have = load_counts(rd)
    if counts.empty:
        print("REFUSED: no session-setup run is ingested yet (R097, R098).")
        return 2
    cfg = config()
    fm = FillModel.load("assumed")
    slip = {"entry": fm.entry_slippage_ticks, "stop": fm.stop_slippage_ticks, "flatten": fm.flatten_slippage_ticks}
    variants = score(counts, cfg, dict(fm.round_turn_by_instrument), slip, load_baseline(rd, cfg))
    k = grid_k(cfg)
    summary = {"section": "summary", "k": k, "variants_with_trades": len(variants), "markets_ingested": ",".join(have),
               "eligible": int(variants["eligible"].sum()),
               "positive_selection_bound": int((variants["eligible"] & (variants["sel_e_gross_lower_bound"] > 0)).sum()),
               "shortlisted": int(variants["shortlisted"].sum()), "survivors": int(variants["survives"].sum())}
    out = pd.concat([variants, directions(counts, variants, cfg, dict(fm.round_turn_by_instrument), slip),
                     windows(variants), pd.DataFrame([summary])], ignore_index=True)
    write_result(out, "session_setups_score", script=SCRIPT, seed=None, require_seed=False, exploratory=True,
                 results_dir=results_dir,
                 parameters={"screen": cfg["screen"], "windows": cfg["windows"], "rules": cfg["rules"],
                             "stops_range": cfg["stops_range"], "rr": cfg["rr"], "k": k, "slippage_ticks": slip,
                             "fees": dict(fm.round_turn_by_instrument), "markets_ingested": have,
                             "markets_missing": sorted(set(MARKETS) - set(have)),
                             "runs": {m: SETUP_RUNS[m] for m in have}, "decision": "D-245, D-246"},
                 notes={"status": "EXPLORATORY: T15 item 8, the session-setup screen scored by rules fixed before "
                                  "the counts were read (D-245, D-246); a survivor becomes a model card, never a "
                                  "result"},
                 description="EXPLORATORY: the session-setup screen SS1 -- per market, window, rule, stop and R the net "
                             "edge per trade selected on 2009-2019 and validated on 2020-2025, with k. No seed: a "
                             "deterministic reading of counts.")
    if record:
        VariantCounter().record(prereg_id="D-245:session_setups_screen", seed=0, exploratory=True,
                                params={"study": "session-setup screen SS1", "k": k, "markets": have},
                                label="EXPLORATORY: six windows x eleven rules x three stops x four R per market "
                                      "(deterministic counts; the seed is nominal)")
    pd.set_option("display.width", 250)
    print(pd.DataFrame([summary]).to_string(index=False))
    print(windows(variants)[["market", "window", "eligible", "positive_selection_bound", "best_rule",
                             "best_sel_e_gross_lower_bound", "best_val_e_net"]].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
