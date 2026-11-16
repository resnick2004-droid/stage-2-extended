"""Score the opening-gap reversal design (D-105 to D-109) on the development evidence.

    python scripts/score_gap_reversal.py

Refuses unless docs/data_reports/gap_reversal_evidence.md carries a verdict without BLOCK, and
raises if any bar lies on or after the confirmation boundary. Everything is fixed by
config/gap_reversal.yaml; this script only executes it. Writes, each with a manifest:

  results/gap_gate.csv      stage 1: the gate on gap-up days (whole, per half), gap-downs, Mondays,
                            per year, and the ACAR path
  results/gap_grid.csv      stage 2: the 12 variants x {selection, validation} x {P_ref, actual},
                            eligibility and the selection
  results/gap_null.csv      the permutation best-of-12 lower bounds and the real one
  results/gap_selected.csv  the selected variant: validation, sensitivities, go/no-go items
  results/gap_trades.csv    every scored day for every variant at P_ref and actual, with u
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
from propedge.outcomes import gap_reversal as gr  # noqa: E402
from propedge.reporting.results import read_result, write_result  # noqa: E402

EVIDENCE = ROOT / "results" / "manual_R027_gap_ES2.csv"
REPORT = ROOT / "docs" / "data_reports" / "gap_reversal_evidence.md"
SCRIPT = "scripts/score_gap_reversal.py"


def _integrity_passed() -> bool:
    if not REPORT.is_file():
        return False
    text = REPORT.read_text(encoding="utf-8")
    return "## Verdict" in text and "BLOCK" not in text.split("## Verdict")[-1]


def _gate_rows(p, status, cfg, mask, scope):
    g = gr.gate(p, status, cfg, mask)
    rows = [{"table": "gate", "scope": scope, **{k: v for k, v in g.items() if k != "acar"}}]
    rows += [{"table": "acar", "scope": scope, "minute": m, "acar_pct": v}
             for m, v in g["acar"].items()]
    return rows, g


def main() -> int:
    t0 = time.time()
    if not _integrity_passed():
        print(f"REFUSED: no passing data-integrity verdict in {REPORT.relative_to(ROOT)}.")
        return 2
    cfg = gr.load_design()
    fills = gr.fills_from_config("assumed", cfg["instrument"]["vehicle"])
    bars = read_result(EVIDENCE)
    assert_development_only(pd.to_datetime(bars["d"].astype(str), format="%Y%m%d"),
                            what="gap-reversal evidence")
    p = gr.panel_from_bars(bars)
    status = gr.day_status(p, cfg)
    dev = cfg["development"]
    in_sel = (status["date"] <= pd.Timestamp(dev["selection_end"])).to_numpy()
    in_val = (status["date"] >= pd.Timestamp(dev["validation_start"])).to_numpy()
    p_ref = float(cfg["scale"]["selection_price_level"])
    b = cfg["search"]
    block, reps, seed = cfg["gate"]["bootstrap"]["block_days"], 10_000, b["selection_seed"]

    # ------------------------------------------------------------ stage 1: the gate
    up = gr.event_mask(status, cfg)
    gate_rows, g_all = _gate_rows(p, status, cfg, up, "up|whole")
    for scope, mask in (("up|selection_half", up & in_sel), ("up|validation_half", up & in_val),
                        ("down|whole", gr.event_mask(status, cfg, sign="down_only")),
                        ("monday_up|whole", gr.event_mask(status, cfg, weekdays=["Mon"]))):
        gate_rows += _gate_rows(p, status, cfg, mask, scope)[0]
    for y in sorted(status["date"].dt.year.unique()):
        gate_rows += _gate_rows(p, status, cfg, up & (status["date"].dt.year == y).to_numpy(),
                                f"up|{y}")[0]
    rel = status["release_flag"].to_numpy()
    gate_rows += _gate_rows(p, status, cfg, up & rel, "up|release_flag")[0]
    gate_rows += _gate_rows(p, status, cfg, up & ~rel, "up|no_release_flag")[0]
    # D-108(a): every recorded day with its status, so the campaign clock can run on calendar days
    days_out = status.assign(event_up=up, event_down=gr.event_mask(status, cfg, sign="down_only"),
                             selection_half=in_sel)
    print(f"gate: n={g_all['n_days']} G={g_all['G']:.4f}% lb={g_all['G_lb']:.4f}% "
          f"({g_all['G_over_grant']:.2f} x Grant) -> {'PASS' if g_all['passes'] else 'FAIL'}")

    # ------------------------------------------------------------ stage 2: the grid
    days = np.flatnonzero(up)
    dirs = gr.against_the_gap(status)[days]
    vs = gr.variants(cfg)
    counter = VariantCounter()
    trades, grid_rows, u_minus, u_plus = [], [], {}, {}
    for v in vs:
        counter.record(prereg_id="T4:gap_reversal:development", params={**v, "design": "D-105"},
                       seed=seed, label="development search, not a test")
        at_ref = gr.score_variant(p, status, days, dirs, v, cfg, fills, scale_to=p_ref)
        at_act = gr.score_variant(p, status, days, dirs, v, cfg, fills)
        flipped = gr.score_variant(p, status, days, -dirs, v, cfg, fills, scale_to=p_ref)
        at_ref["half"] = np.where(in_sel[days], "selection", "validation")
        at_act["half"] = at_ref["half"].to_numpy()
        trades += [at_ref, at_act]
        sel_mask = in_sel[days]
        u_minus[v["key"]] = at_ref.loc[sel_mask, "u"].to_numpy()
        u_plus[v["key"]] = flipped.loc[sel_mask, "u"].to_numpy()
        for scale, tab in (("P_ref", at_ref), ("actual", at_act)):
            for half in ("selection", "validation"):
                s = gr.stats(tab[tab["half"] == half], block=block, reps=reps, seed=seed)
                grid_rows.append({"variant": v["key"], "kind": v["kind"], "w": v["w"], "m": v["m"],
                                  "scale": scale, "half": half, **s})
        print(f"  {v['key']:<22} scored  ({time.time() - t0:5.0f} s)")
    grid = pd.DataFrame(grid_rows)
    sel_rows = grid[(grid["scale"] == "P_ref") & (grid["half"] == "selection")]
    choice = gr.select(sel_rows.to_dict("records"), cfg)
    grid["eligible"] = [choice["eligible"].get((r.kind, r.w, r.m), False) for r in grid.itertuples()]
    chosen = choice["selected"]
    grid["selected"] = [(r.kind, r.w, r.m) == chosen for r in grid.itertuples()]
    print(f"selection: {chosen} -- {choice['why']}")

    # ------------------------------------------------------------ the permutation null
    pn = b["permutation_null"]
    null = gr.permutation_null(u_minus, u_plus, permutations=pn["permutations"], seed=pn["seed"],
                               block=block, reps=reps, boot_seed=pn["seed"] + 1000)
    real_best = float(sel_rows["lb"].max())
    q95 = float(np.quantile(null, 0.95))
    null_rows = [{"permutation": k + 1, "best_of_12_lb": float(x)} for k, x in enumerate(null)]
    null_rows.append({"permutation": 0, "best_of_12_lb": real_best, "note": "REAL"})
    cleared = real_best > q95
    print(f"null: real best-of-12 lb={real_best:.4f} vs 95th pct {q95:.4f} -> "
          f"{'cleared' if cleared else 'NOT cleared'}  ({time.time() - t0:.0f} s)")

    # ------------------------------------------------------------ the selected variant
    sel_out = []
    if chosen is not None:
        v = next(x for x in vs if (x["kind"], x["w"], x["m"]) == chosen)
        val_ref = grid[(grid["variant"] == v["key"]) & (grid["scale"] == "P_ref")
                       & (grid["half"] == "validation")].iloc[0]
        val_act = grid[(grid["variant"] == v["key"]) & (grid["scale"] == "actual")
                       & (grid["half"] == "validation")].iloc[0]
        for label, row in (("validation|P_ref", val_ref), ("validation|actual", val_act)):
            sel_out.append({"item": label, "n": row["n"], "mean": row["mean"], "sd": row["sd"],
                            "lb": row["lb"], "floor_bound_share": row["floor_bound_share"],
                            "p_target": row["p_target"], "p_stop": row["p_stop"],
                            "p_time": row["p_time"]})
        for scale_name, scale_to in (("P_ref", p_ref), ("actual", None), ("2000", 2000.0),
                                     ("6500", 6500.0)):
            tab = gr.score_variant(p, status, days, dirs, v, cfg, fills, scale_to=scale_to)
            s = gr.stats(tab, block=block, reps=reps, seed=seed)
            sel_out.append({"item": f"whole|{scale_name}", "n": s["n"], "mean": s["mean"],
                            "sd": s["sd"], "lb": s["lb"], "floor_bound_share": s["floor_bound_share"],
                            "p_target": s["p_target"], "p_stop": s["p_stop"], "p_time": s["p_time"]})
        sens = {"threshold_0.10": dict(threshold=0.10), "threshold_0.30": dict(threshold=0.30),
                "sign_down_only": dict(sign="down_only"), "sign_both": dict(sign="both"),
                "monday_only": dict(weekdays=["Mon"])}
        for name, kw in sens.items():
            m = gr.event_mask(status, cfg, **kw)
            dd = np.flatnonzero(m)
            tab = gr.score_variant(p, status, dd, gr.against_the_gap(status)[dd], v, cfg, fills,
                                   scale_to=p_ref)
            s = gr.stats(tab, block=block, reps=reps, seed=seed)
            sel_out.append({"item": f"sensitivity|{name}|P_ref", "n": s["n"], "mean": s["mean"],
                            "sd": s["sd"], "lb": s["lb"]})
        whole = gr.score_variant(p, status, days, dirs, v, cfg, fills, scale_to=p_ref)
        for flag in (True, False):
            s = gr.stats(whole[whole["release_flag"] == flag], block=block, reps=reps, seed=seed)
            sel_out.append({"item": f"release_flag_{flag}|P_ref", "n": s["n"], "mean": s["mean"],
                            "sd": s["sd"], "lb": s["lb"]})
        for y, tab in whole.groupby(whole["date"].dt.year):
            s = gr.stats(tab, block=block, reps=reps, seed=seed)
            sel_out.append({"item": f"year_{y}|P_ref", "n": s["n"], "mean": s["mean"],
                            "sd": s["sd"], "lb": s["lb"]})
        fb = cfg["stop"]["fallback_if_floor_bound"]
        floor_share = float(sel_rows[sel_rows["variant"] == v["key"]]["floor_bound_share"].iloc[0])
        fallback = floor_share > fb["floor_bound_share_above"]
        go = {"gate_passed": bool(g_all["passes"]), "null_cleared": bool(cleared),
              "validation_mean_nonneg": bool(val_ref["mean"] >= 0),
              "floor_bound_share_selection": floor_share, "fallback_applied": bool(fallback),
              "pre_registered_multiplier": fb["multiplier"] if fallback else v["m"],
              "all_computable_items_met": bool(g_all["passes"] and cleared and val_ref["mean"] >= 0),
              "operator_decision": "pending"}
    else:
        go = {"gate_passed": bool(g_all["passes"]), "null_cleared": bool(cleared),
              "validation_mean_nonneg": False, "all_computable_items_met": False,
              "operator_decision": "pending", "note": "no eligible variant"}
    sel_out += [{"item": f"go_no_go|{k}", "value": v} for k, v in go.items()]

    # ------------------------------------------------------------ trigger diagnostic
    entry = gr.slot_of(cfg["timing"]["entry_earliest_ct"].replace(":", ""))
    for v in vs:
        if v["m"] != cfg["stop"]["multiplier_grid"][0]:
            continue
        tab = next(t for t in trades if t["variant"].iloc[0] == v["key"] and t["scale"].iloc[0] == "actual")
        fav = []
        for r in tab[tab["u"].notna()].itertuples():
            i = int(np.flatnonzero(p.n == r.n)[0])
            c = gr._ffill(p.c[i])
            j = min(int(r.t) + 45, gr.SLOTS - 1)
            fav.append(100.0 * r.direction * np.log(c[j] / c[int(r.t)]))
        sel_out.append({"item": f"trigger_diag|{v['kind']}|w{v['w']}", "n": len(fav),
                        "mean": float(np.mean(fav)) if fav else np.nan,
                        "sd": float(np.std(fav, ddof=1)) if len(fav) > 1 else np.nan})

    # ------------------------------------------------------------ write
    params = {"design": "config/gap_reversal.yaml", "evidence": str(EVIDENCE.relative_to(ROOT)),
              "fill_profile": "assumed", "vehicle": cfg["instrument"]["vehicle"],
              "selection_price_level": p_ref, "block_days": block, "replicates": reps,
              "variants": [v["key"] for v in vs], "k": len(vs)}
    notes = {"status": "development search; no confirmation data; not a test of the edge",
             "costs": "assumed profile, flagged as an assumption (D-95)",
             "scale": "P_ref rows are the day's prices rescaled to the stated level before costs (D-106)"}
    write_result(pd.DataFrame(gate_rows), "gap_gate", script=SCRIPT, seed=cfg["gate"]["bootstrap"]["seed"],
                 parameters=params, notes=notes, variant_count=len(vs),
                 description="Stage 1 existence gate for the opening-gap reversal: favourable ACAR "
                             "after the 08:40 entry on gap-up non-Monday days, development data.")
    write_result(grid, "gap_grid", script=SCRIPT, seed=seed, parameters=params, notes=notes,
                 variant_count=len(vs),
                 description="Stage 2 grid: 12 variants x half x scale, selection statistics, "
                             "plateau eligibility and the selection (D-105).")
    write_result(pd.DataFrame(null_rows), "gap_null", script=SCRIPT, seed=pn["seed"],
                 parameters={**params, "permutations": pn["permutations"]}, notes=notes,
                 variant_count=len(vs),
                 description="Direction-flip permutation null: best-of-12 selection-half lower "
                             "bound per permutation, and the real one (permutation 0).")
    write_result(pd.DataFrame(sel_out), "gap_selected", script=SCRIPT, seed=seed, parameters=params,
                 notes={**notes, "selection": str(chosen), "why": choice["why"]},
                 variant_count=len(vs),
                 description="The selected variant: validation half, whole-development scales, "
                             "sensitivities, trigger diagnostic and the go/no-go items.")
    write_result(pd.concat(trades, ignore_index=True), "gap_trades", script=SCRIPT, seed=seed,
                 parameters=params, notes=notes, variant_count=len(vs),
                 description="Every scored event day for every variant at P_ref and actual scale.")
    write_result(days_out, "gap_days", script=SCRIPT, seed=seed, parameters=params, notes=notes,
                 variant_count=len(vs), require_seed=False,
                 description="Every recorded development day with its gap, its skip reason, its "
                             "event flags and its release flag (D-108a). Deterministic.")
    print(pd.DataFrame(sel_out).to_string(index=False, max_colwidth=40))
    print(f"done in {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
