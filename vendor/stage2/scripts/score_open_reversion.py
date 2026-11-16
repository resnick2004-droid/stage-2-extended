"""Score the reversion-to-the-open design (config/open_reversion.yaml) on the development evidence.

    python scripts/score_open_reversion.py

Refuses unless the design's `status` is `fixed` (a DECISIONS.md entry fixes it once 2B's prior is
in), unless docs/data_reports/gap_reversal_evidence.md (the same evidence file) carries a verdict
without BLOCK, and raises if any bar lies on or after the confirmation boundary. Writes, each with
a manifest:

  results/openrev_gate.csv      stage 1: the slope gate (whole, per half, by side, by weekday, by year,
                                10-minute setup sensitivity)
  results/openrev_grid.csv      stage 2: 6 variants and their plain-entry baselines x half x scale
  results/openrev_null.csv      the geometry-flip permutation null and the real best-of-6
  results/openrev_selected.csv  the selected variant: validation, sensitivities, go/no-go items
  results/openrev_trades.csv    every scored day for every variant and baseline at P_ref and actual
  results/openrev_days.csv      every recorded day with its status (D-108a)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from propedge.backtest.harness import VariantCounter  # noqa: E402
from propedge.data.window import assert_development_only  # noqa: E402
from propedge.outcomes import open_reversion as orv  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

REPORT = ROOT / "docs" / "data_reports" / "gap_reversal_evidence.md"
SCRIPT = "scripts/score_open_reversion.py"


def _integrity_passed() -> bool:
    if not REPORT.is_file():
        return False
    text = REPORT.read_text(encoding="utf-8")
    return "## Verdict" in text and "BLOCK" not in text.split("## Verdict")[-1]


def main() -> int:
    t0 = time.time()
    cfg = orv.load_design()
    if cfg.get("status") not in ("fixed", "exploratory"):
        print(f"REFUSED: config/open_reversion.yaml status is {cfg.get('status')!r}; the design is "
              "fixed by a DECISIONS.md entry once 2B's prior is in, or run as exploratory by one.")
        return 2
    exploratory = cfg["status"] == "exploratory"
    if not _integrity_passed():
        print(f"REFUSED: no passing data-integrity verdict in {REPORT.relative_to(ROOT)}.")
        return 2
    evidence = ROOT / cfg["source"]["evidence"]
    bars = read_result(evidence)
    assert_development_only(pd.to_datetime(bars["d"].astype(str), format="%Y%m%d"),
                            what="open-reversion evidence")
    p = orv.panel_from_bars(bars)
    status = orv.day_status(p)
    dev = cfg["development"]
    in_sel = (status["date"] <= pd.Timestamp(dev["selection_end"])).to_numpy()
    in_val = (status["date"] >= pd.Timestamp(dev["validation_start"])).to_numpy()
    ok = status["reason"].to_numpy() == ""
    days_all = np.flatnonzero(ok)
    p_ref = float(cfg["scale"]["selection_price_level"])
    block, reps, seed = cfg["gate"]["bootstrap"]["block_days"], 10_000, cfg["search"]["selection_seed"]
    fills = orv.fills_from_config("assumed", cfg["instrument"]["vehicle"])

    # ------------------------------------------------------------ stage 1: the gate
    gate_rows = []

    def add_gate(scope, mask, **kw):
        g = orv.gate(p, cfg, np.flatnonzero(mask), **kw)
        gate_rows.append({"scope": scope, **g})
        return g

    g_all = add_gate("all|whole", ok)
    add_gate("all|selection_half", ok & in_sel)
    add_gate("all|validation_half", ok & in_val)
    add_gate("all|setup_10min", ok, setup_end="0840")
    x = orv.excursion_and_returns(p, days_all)
    above = status["n"].isin(x.loc[x["x"] > 0, "n"]).to_numpy()
    add_gate("above_open|whole", ok & above)
    add_gate("below_open|whole", ok & ~above)
    for wd in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
        add_gate(f"weekday_{wd}", ok & (status["weekday"] == wd).to_numpy())
    for y in sorted(status["date"].dt.year.unique()):
        add_gate(f"year_{y}", ok & (status["date"].dt.year == y).to_numpy())
    print(f"gate: n={g_all['n_days']} beta45={g_all['beta_45']:.4f} ub95={g_all['beta_45_ub95']:.4f} "
          f"effect={g_all['effect_size_pct']:.4f}% -> {'PASS' if g_all['passes'] else 'FAIL'}")

    # ------------------------------------------------------------ stage 2: the grid
    vs = orv.variants(cfg)
    counter = VariantCounter()
    trades, grid_rows, u_real, u_flip = [], [], {}, {}
    for v in vs:
        counter.record(prereg_id="T4:open_reversion:development", params={**v, "design": "open_reversion"},
                       seed=seed, label="development search, not a test")
        for baseline in (False, True):
            at_ref = orv.score_variant(p, status, days_all, v, cfg, fills, scale_to=p_ref, baseline=baseline)
            at_act = orv.score_variant(p, status, days_all, v, cfg, fills, baseline=baseline)
            at_ref["half"] = np.where(in_sel[days_all], "selection", "validation")
            at_act["half"] = at_ref["half"].to_numpy()
            trades += [at_ref, at_act]
            for scale, tab in (("P_ref", at_ref), ("actual", at_act)):
                for half in ("selection", "validation"):
                    s = orv.stats(tab[tab["half"] == half], block=block, reps=reps, seed=seed)
                    grid_rows.append({"variant": v["key"], "anchor": v["anchor"], "r_min": v["r_min"],
                                      "baseline": baseline, "scale": scale, "half": half, **s})
            if not baseline:
                flipped = orv.score_variant(p, status, days_all, v, cfg, fills, scale_to=p_ref, flip=True)
                sel = in_sel[days_all]
                u_real[v["key"]] = at_ref.loc[sel, "u"].to_numpy()
                u_flip[v["key"]] = flipped.loc[sel, "u"].to_numpy()
        print(f"  {v['key']:<22} scored  ({time.time() - t0:5.0f} s)")
    grid = pd.DataFrame(grid_rows)
    sel_rows = grid[(grid["scale"] == "P_ref") & (grid["half"] == "selection")]
    choice = orv.select(sel_rows.to_dict("records"), cfg)
    chosen = choice["selected"]
    grid["eligible"] = [choice["eligible"].get((r.anchor, r.r_min), False) and not r.baseline
                        for r in grid.itertuples()]
    grid["selected"] = [(r.anchor, r.r_min) == chosen and not r.baseline for r in grid.itertuples()]
    print(f"selection: {chosen} -- {choice['why']}")

    # ------------------------------------------------------------ the permutation null
    pn = cfg["search"]["permutation_null"]
    null = orv.permutation_null(u_real, u_flip, permutations=pn["permutations"], seed=pn["seed"],
                                block=block, reps=reps, boot_seed=pn["seed"] + 1000)
    real_best = float(sel_rows[~sel_rows["baseline"]]["lb"].max())
    q95 = float(np.quantile(null, 0.95))
    cleared = real_best > q95
    null_rows = [{"permutation": k + 1, "best_lb": float(z)} for k, z in enumerate(null)]
    null_rows.append({"permutation": 0, "best_lb": real_best, "note": "REAL"})
    print(f"null: real best lb={real_best:.4f} vs 95th pct {q95:.4f} -> {'cleared' if cleared else 'NOT cleared'}")

    # ------------------------------------------------------------ the selected variant
    sel_out = []
    if chosen is not None:
        v = next(z for z in vs if (z["anchor"], z["r_min"]) == chosen)
        val = grid[(grid["variant"] == v["key"]) & ~grid["baseline"] & (grid["half"] == "validation")]
        for r in val.itertuples():
            sel_out.append({"item": f"validation|{r.scale}", "n": r.n, "mean": r.mean, "sd": r.sd, "lb": r.lb,
                            "win_over_loss": r.win_over_loss, "p_target": r.p_target, "p_stop": r.p_stop,
                            "p_time": r.p_time, "floor_bound_share": r.floor_bound_share})
        for name, scale_to in (("P_ref", p_ref), ("actual", None), ("2000", 2000.0), ("6500", 6500.0)):
            s = orv.stats(orv.score_variant(p, status, days_all, v, cfg, fills, scale_to=scale_to),
                          block=block, reps=reps, seed=seed)
            sel_out.append({"item": f"whole|{name}", **{k: s[k] for k in ("n", "mean", "sd", "lb", "win_over_loss",
                                                                        "p_target", "p_stop", "p_time",
                                                                        "floor_bound_share", "mean_R_at_entry")}})
        whole = orv.score_variant(p, status, days_all, v, cfg, fills, scale_to=p_ref)
        for label, sub in (("side_short", whole["direction"] == -1), ("side_long", whole["direction"] == 1)):
            s = orv.stats(whole[sub], block=block, reps=reps, seed=seed)
            sel_out.append({"item": f"{label}|P_ref", "n": s["n"], "mean": s["mean"], "sd": s["sd"], "lb": s["lb"]})
        for y, tab in whole.groupby(whole["date"].dt.year):
            s = orv.stats(tab, block=block, reps=reps, seed=seed)
            sel_out.append({"item": f"year_{y}|P_ref", "n": s["n"], "mean": s["mean"], "sd": s["sd"], "lb": s["lb"]})
        wide = orv.score_variant(p, status, days_all, v, {**cfg, "trigger": {**cfg["trigger"],
                                 "window_ct": cfg["trigger"]["window_sensitivity_ct"]}}, fills, scale_to=p_ref)
        s = orv.stats(wide, block=block, reps=reps, seed=seed)
        sel_out.append({"item": "sensitivity|window_to_10:00|P_ref", "n": s["n"], "mean": s["mean"],
                        "sd": s["sd"], "lb": s["lb"]})
        srow = sel_rows[(sel_rows["variant"] == v["key"]) & ~sel_rows["baseline"]].iloc[0]
        vrow = val[val["scale"] == "P_ref"].iloc[0]
        fallback = float(srow["floor_bound_share"]) > 0.8
        go = {"gate_passed": bool(g_all["passes"]), "null_cleared": bool(cleared),
              "validation_mean_nonneg": bool(vrow["mean"] >= 0),
              "realised_win_over_loss_above_1": bool(vrow["win_over_loss"] > 1),
              "floor_bound_share_selection": float(srow["floor_bound_share"]), "fallback_applied": fallback,
              "all_computable_items_met": bool(g_all["passes"] and cleared and vrow["mean"] >= 0
                                               and vrow["win_over_loss"] > 1),
              "operator_decision": "pending"}
    else:
        go = {"gate_passed": bool(g_all["passes"]), "null_cleared": bool(cleared),
              "all_computable_items_met": False, "operator_decision": "pending", "note": "no eligible variant"}
    if exploratory:
        go["eligible_for_confirmation"] = False
        go["label"] = "EXPLORATORY (D-118): no published prior; learning exercise"
    sel_out += [{"item": f"go_no_go|{k}", "value": z} for k, z in go.items()]

    # ------------------------------------------------------------ write
    params = {"design": "config/open_reversion.yaml", "evidence": str(evidence.relative_to(ROOT)),
              "fill_profile": "assumed", "vehicle": cfg["instrument"]["vehicle"],
              "selection_price_level": p_ref, "block_days": block, "replicates": reps,
              "variants": [v["key"] for v in vs], "k": len(vs), "baselines": len(vs)}
    notes = {"status": "development search; no confirmation data; not a test of the edge",
             "costs": "assumed profile, flagged as an assumption (D-95)",
             "scale": "P_ref rows are the day's prices rescaled to the stated level before costs (D-106)",
             "written_after": "the gap-reversal results on the same evidence (D-112)",
             "exploratory": "D-118: no published prior; learning exercise; never eligible for confirmation"}
    write_result(pd.DataFrame(gate_rows), "openrev_gate", script=SCRIPT, seed=cfg["gate"]["bootstrap"]["seed"],
                 parameters=params, notes=notes, variant_count=len(vs), exploratory=exploratory,
                 description="Stage 1 slope gate for reversion toward the open: OLS slope of the next 30/45/60-minute "
                             "return on the first-15-minute move, all scoreable days, development data.")
    write_result(grid, "openrev_grid", script=SCRIPT, seed=seed, parameters=params, notes=notes,
                 variant_count=len(vs), exploratory=exploratory, description="Stage 2 grid: 6 variants and plain-entry baselines x half x scale.")
    write_result(pd.DataFrame(null_rows), "openrev_null", script=SCRIPT, seed=pn["seed"],
                 parameters={**params, "permutations": pn["permutations"]}, notes=notes, variant_count=len(vs), exploratory=exploratory,
                 description="Geometry-flip permutation null: best-of-6 selection-half lower bound per permutation.")
    write_result(pd.DataFrame(sel_out), "openrev_selected", script=SCRIPT, seed=seed, parameters=params,
                 notes={**notes, "selection": str(chosen), "why": choice["why"]}, variant_count=len(vs), exploratory=exploratory,
                 description="The selected variant: validation, scales, sides, years, window sensitivity, go/no-go.")
    write_result(pd.concat(trades, ignore_index=True), "openrev_trades", script=SCRIPT, seed=seed,
                 parameters=params, notes=notes, variant_count=len(vs), exploratory=exploratory,
                 description="Every scored day for every variant and baseline at P_ref and actual scale.")
    write_result(status.assign(selection_half=in_sel), "openrev_days", script=SCRIPT, seed=seed,
                 parameters=params, notes=notes, variant_count=len(vs), exploratory=exploratory, require_seed=False,
                 description="Every recorded development day with its status (D-108a). Deterministic.")
    print(pd.DataFrame(sel_out).to_string(index=False, max_colwidth=40))
    print(f"done in {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
