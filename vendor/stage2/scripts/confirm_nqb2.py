"""NQB2's one confirmation verdict (D-242), under its registered pre-registration -- the rules of
config/nqb2_confirmation.yaml applied to the held-back year's counts, once.

    python scripts/confirm_nqb2.py

Reads the ingested confirmation kit (`regime_kit.CONFIRM_RUNS`, `results/manual_R095_regime_confirm_NQ_2026.csv`, or
R096's after an unusable R095) and applies, in order, what the pre-registration fixed before any of the window was
read:

1. **Resolution (D-212)**: per leg (the Combine's 2:1 bracket on 20 points, the funded account's 1.5:1 on 40), pooled
   over the registered decision slots on full sessions, the share of brackets at their target or stop is at least
   `resolved_share_min` overall and in each calendar year of the window (2025 from July, 2026 to June).
2. **The D-145 gate at D-234's 0 %**: each leg's net edge per trade from the counts -- a target pays R, a stop costs 1,
   a bracket open at the flatten counts as a full loss, less D-238's cost (D-221's with the measured overshoot,
   `regime_then_now.cost_per_micro`) -- at its lower bound (the twelve monthly estimates' mean less the one-sided 95 %
   t quantile with months - 1 degrees of freedom times their standard error), through the campaign
   (`today_noedge_campaign.campaign`: `s1_low_edge`, one Combine live, one trade a day per account, five accounts, the
   bankroll, horizon, paths and seed) at 0 % denial: median log growth above zero.

PASS is both; anything else is FAIL. Beside it, never instead: the point estimates, five Combines live, 10, 25 and 50 %
denial (in the file, D-236), ruin, drawdown, the first payout, RTP placement, each leg's break-even hit rate and bound at
0.05/N, the realised per-trade sd, and the old gate (e >= 0.10 net, bound >= 0.05; failed by construction). Writes
results/nqb2_confirmation.csv. Refuses unless the config's pre-registration is a runnable row of prereg/REGISTRY.md and
the confirmation run is ingested; refuses a second verdict (the window is read once).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import no_edge_contract as nec  # noqa: E402
import today_noedge_campaign as tnc  # noqa: E402

SCRIPT = "scripts/confirm_nqb2.py"
RESULT = "nqb2_confirmation"
LEGS = ("combine", "funded")


def config_matches_the_engine(c: dict) -> list[str]:
    """The registered campaign settings are the ones the campaign code runs; any difference is refused."""
    k = c["campaign"]
    want = {"accounts": nec.ACCOUNTS, "bankroll": nec.BANKROLL, "horizon_days": nec.HORIZON, "seed": nec.SEED,
            "gate_denial": 0.0, "rtp_warnings": 0, "trades_per_day": 1, "open_bracket": "loss"}
    out = [f"campaign.{key} is {k.get(key)!r}, the code runs {v!r}" for key, v in want.items() if k.get(key) != v]
    protocol, _ = nec.arm(k["arm"])
    code = {"combine": (float(protocol.combine_rr), float(protocol.combine_risk)),
            "funded": (float(protocol.funded_rr), float(protocol.funded_risk))}
    legs = {name: (float(v["R"]), float(v["risk"])) for name, v in c["legs"].items()}
    if legs != code:
        out.append(f"legs (R, risk) {legs} are not arm {k['arm']}'s {code}")
    if int(protocol.trades_per_day) != int(k["trades_per_day"]):
        out.append(f"arm {k['arm']} trades {protocol.trades_per_day} a day, the config {k['trades_per_day']}")
    return out


def chosen_run(results_dir: Path, runs_dir: Path, c: dict) -> tuple[str | None, str | None]:
    """D-230: (the run the verdict reads, None) -- or (None, why there is nothing to read yet), or ('UNUSABLE', why)
    when both permitted runs were unusable, which is a FAIL. The fix runs only after the first run is unusable."""
    first, second = c["runs"]
    ingested = [r for r in c["runs"] if (results_dir / f"manual_{r.replace('-', '_')}.csv").is_file()]
    unusable = [r for r in c["runs"] if (runs_dir / r / "unusable.json").is_file()]
    both = sorted(set(ingested) & set(unusable))
    if both:
        return None, f"{', '.join(both)} is recorded unusable and also ingested; an unusable run is never read"
    if len(ingested) > 1:
        return None, "both permitted runs are ingested; the window is read once"
    if ingested:
        if ingested[0] == second and first not in unusable:
            return None, f"{second} is ingested but {first} is not recorded unusable; the fix runs only after it"
        return ingested[0], None
    if len(unusable) == 2:
        return "UNUSABLE", "both permitted runs were unusable (D-230)"
    return None, "the confirmation run is not ingested"


def resolution(cnt: pd.DataFrame, c: dict) -> pd.DataFrame:
    """Rule 1: per leg, overall and in each registered year, the share resolved at the registered slots; a registered
    year with no brackets fails (D-230)."""
    floor = float(c["resolved_share_min"])
    x = cnt[(cnt["kind"] == "count") & cnt["decision_slot"].isin([int(s) for s in c["decision_slots"]])]
    rows = []
    for leg in LEGS:
        g = x[x["leg"] == leg]
        for year, gy in [("all", g)] + [(int(y), g[g["year"] == y]) for y in c["years"]]:
            n, t, s = int(gy["n"].sum()), int(gy["target"].sum()), int(gy["stop"].sum())
            share = (t + s) / n if n else float("nan")
            rows.append({"section": "resolution", "leg": leg, "year": year, "n": n, "resolved_share": share,
                         "passes": bool(n and share >= floor)})
    return pd.DataFrame(rows)


def _reading(c: pd.DataFrame, sp: pd.DataFrame, R: float, stop_points: float, q: dict, fee: float, slip: dict) -> dict:
    """A leg's shares, cost and net edge from its count rows `c` and the slots' spread rows `sp`."""
    from regime_then_now import cost_per_micro

    tick_dollars = q["micro_tick"] * q["micro_point_value"]
    n, t, s, o = (int(c[k].sum()) for k in ("n", "target", "stop", "open"))
    qn = float(sp["spread_count"].sum())
    spread = float((sp["spread_ticks_mean"].astype(float) * sp["spread_count"].astype(float)).sum()) / qn if qn else \
        float("nan")
    over = float(c["overshoot_ticks_sum"].astype(float).sum()) / s if s else 0.0     # each leg's stop exits
    cost_r = cost_per_micro(fee, tick_dollars, spread, s / n, o / n, over, slip) / (stop_points * q["micro_point_value"])
    gross = (t * R - s - o) / n
    sd = math.sqrt(max((t * R * R + s + o) / n - gross * gross, 0.0))       # +R, -1, -1 (open lost)
    return {"n": n, "target_share": t / n, "stop_share": s / n, "open_share": o / n, "spread_ticks_mean": spread,
            "overshoot_ticks_per_exit": over, "e_gross": gross, "cost_r": cost_r, "e_net": gross - cost_r,
            "per_trade_sd": sd}


def leg_edges(cnt: pd.DataFrame, c: dict, q: dict, tq: float) -> pd.DataFrame:
    """Per leg, per registered month and pooled: shares, cost and net edge; the pooled row carries the lower bound."""
    slip, fees = tnc._slip_fees()
    fee = float(fees[q["micro"]])
    slots = [int(s) for s in c["decision_slots"]]
    x = cnt[(cnt["kind"] == "count") & cnt["decision_slot"].isin(slots)]
    sp = cnt[(cnt["kind"] == "spread") & cnt["decision_slot"].isin(slots)]
    rows = []
    for leg in LEGS:
        R, stop = float(c["legs"][leg]["R"]), float(c["legs"][leg]["stop_points"])
        g = x[x["leg"] == leg]
        months = [m for m in c["months"] if len(g[g["month"] == m])]
        for month, gm, sm in [(m, g[g["month"] == m], sp[sp["month"] == m]) for m in months] + [("pooled", g, sp)]:
            rows.append({"section": "inputs", "leg": leg, "month": month, "R": R, "stop_points": stop,
                         **_reading(gm, sm, R, stop, q, fee, slip)})
    out = pd.DataFrame(rows)
    for leg in LEGS:
        y = out[(out["leg"] == leg) & (out["month"] != "pooled")]["e_net"].astype(float)
        sel = (out["leg"] == leg) & (out["month"] == "pooled")
        out.loc[sel, "e_net_lower_bound"] = float(y.mean() - tq * y.std(ddof=1) / math.sqrt(len(y)))
        out.loc[sel, "months"] = len(y)
    return out


def main(results_dir: Path | None = None, n_paths: int | None = None, workers: int = 4,
         runs_dir: Path | None = None) -> int:
    from concurrent.futures import ProcessPoolExecutor

    from scipy import stats

    from propedge import RESULTS_DIR
    from propedge.data.cloud_guard import confirmation_run_authorised
    from propedge.data.regime_kit import confirm_config, confirm_params
    from propedge.data.run_kit import RUNS_DIR
    from propedge.reporting.pin import engine_pin
    from propedge.reporting.results import write_result

    c = confirm_config()
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    if not confirmation_run_authorised(str(c.get("prereg_id"))):
        print(f"REFUSED: {c.get('prereg_id')!r} is not a runnable row of prereg/REGISTRY.md (D-81, D-242).")
        return 2
    bad = config_matches_the_engine(c)
    if bad:
        print("REFUSED: the registered settings and the code differ: " + "; ".join(bad))
        return 2
    if (rd / f"{RESULT}.csv").exists():
        print(f"REFUSED: {RESULT}.csv exists; the held-back window is read once (D-242).")
        return 2
    rdir = Path(runs_dir) if runs_dir is not None else RUNS_DIR
    run, why = chosen_run(rd, rdir, c)
    k = c["campaign"]
    if run == "UNUSABLE":                                   # D-230: two unusable runs are a FAIL, no count read
        out = pd.DataFrame([{"section": "verdict", "verdict": "FAIL", "rule_resolution": False, "rule_gate": False,
                             "reason": why, "prereg": c["prereg_id"]}])
        write_result(out, RESULT, script=SCRIPT, seed=int(k["seed"]), exploratory=False, results_dir=results_dir,
                     provenance={"prereg": c["prereg_id"]},
                     parameters={"config": "config/nqb2_confirmation.yaml", "prereg": c["prereg_id"],
                                 "runs": c["runs"], "decision": "D-242"},
                     notes={"status": f"PRE-REGISTERED ({c['prereg_id']}): FAIL, both permitted runs unusable"},
                     description=f"NQB2's confirmation under {c['prereg_id']}: FAIL, both permitted runs unusable.")
        print(f"VERDICT ({c['prereg_id']}): FAIL -- {why}")
        return 0
    if run is None:
        print(f"REFUSED: {why}.")
        return 2
    src = rd / f"manual_{run.replace('-', '_')}.csv"
    cnt = pd.read_csv(src)
    q = confirm_params(c)
    res = resolution(cnt, c)
    rule1 = bool(res["passes"].all())
    n_months = len([m for m in c["months"] if (cnt["month"] == m).any()])
    tq = float(stats.t.ppf(0.95, n_months - 1))
    inputs = leg_edges(cnt, c, q, tq)
    pooled = inputs[inputs["month"] == "pooled"].set_index("leg")
    lb = (float(pooled.loc["combine", "e_net_lower_bound"]), float(pooled.loc["funded", "e_net_lower_bound"]))
    pt = (float(pooled.loc["combine", "e_net"]), float(pooled.loc["funded", "e_net"]))
    paths, cap, cap5 = int(n_paths or k["n_paths"]), int(k["combines_at_once"]), int(k["beside_combines_at_once"])
    arm, gate_d = k["arm"], float(k["gate_denial"])
    jobs = [(arm, c["market"], *lb, cap, gate_d, "lower_bound", paths)]
    jobs += [(arm, c["market"], *lb, cap, float(d), "lower_bound", paths) for d in k["beside_denials"]]
    jobs += [(arm, c["market"], *pt, cap, gate_d, "point", paths),
             (arm, c["market"], *lb, cap5, gate_d, "lower_bound", paths),
             (arm, c["market"], *pt, cap5, gate_d, "point", paths)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        camp = pd.DataFrame(list(pool.map(tnc.point, jobs)))
    camp["gate_passed"] = pd.NA
    g = (camp["reading"] == "lower_bound") & (camp["denial_p"] == gate_d) & (camp["combines_at_once"] == cap)
    gate_row = camp[g].iloc[0]
    rule2 = bool(gate_row["median_log_growth"] > 0)
    camp.loc[g, "gate_passed"] = rule2
    verdict = "PASS" if rule1 and rule2 else "FAIL"
    old_gate = bool(min(pt) >= 0.10 and min(lb) >= 0.05)
    ing = rdir / run / "ingested.json"
    days = (json.loads(ing.read_text(encoding="utf-8")).get("summary") or {}).get("days") if ing.is_file() else None
    be = {leg: (1.0 + float(pooled.loc[leg, "cost_r"])) / (1.0 + float(c["legs"][leg]["R"])) for leg in LEGS}
    monthly = inputs[inputs["month"] != "pooled"]
    lbN = {}
    if str(c.get("ledger_n")).isdigit():                # beside, never as the verdict: D-189's one-sided 0.05/N
        tN = float(stats.t.ppf(1.0 - 0.05 / int(c["ledger_n"]), n_months - 1))
        lbN = {leg: float(gm["e_net"].astype(float).mean() - tN * gm["e_net"].astype(float).std(ddof=1)
                          / np.sqrt(len(gm))) for leg, gm in monthly.groupby("leg")}
    head = pd.DataFrame([{"section": "verdict", "verdict": verdict, "rule_resolution": rule1, "rule_gate": rule2,
                          "gate_median_log_growth": float(gate_row["median_log_growth"]),
                          "e_combine_lower_bound": lb[0], "e_funded_lower_bound": lb[1], "months": n_months,
                          "t95": tq, "old_gate_met": old_gate, "prereg": c["prereg_id"], "run": run, "days": days,
                          "combine_target_share": float(pooled.loc["combine", "target_share"]),
                          "combine_breakeven_hit": be["combine"],
                          "funded_target_share": float(pooled.loc["funded", "target_share"]),
                          "funded_breakeven_hit": be["funded"],
                          "combine_per_trade_sd": float(pooled.loc["combine", "per_trade_sd"]),
                          "funded_per_trade_sd": float(pooled.loc["funded", "per_trade_sd"]),
                          "beside_e_combine_bound_at_005_over_N": lbN.get("combine", float("nan")),
                          "beside_e_funded_bound_at_005_over_N": lbN.get("funded", float("nan")),
                          "ledger_n": c.get("ledger_n")}])
    out = pd.concat([head, res, inputs, camp], ignore_index=True)
    write_result(out, RESULT, script=SCRIPT, seed=int(k["seed"]), exploratory=False, results_dir=results_dir,
                 provenance={"engine": engine_pin(), "prereg": c["prereg_id"]},
                 parameters={"config": "config/nqb2_confirmation.yaml", "prereg": c["prereg_id"], "source": src.name,
                             "run": run, "months": c["months"], "decision": "D-242", "campaign": k},
                 notes={"status": f"PRE-REGISTERED ({c['prereg_id']}): NQB2's one confirmation, read once"},
                 description=f"NQB2's confirmation under {c['prereg_id']}: resolution on the held-back year and the "
                             "D-145 gate at 0 % denial on its measured inputs; the point estimates, five Combines live "
                             "and the other denials beside it.")
    pd.set_option("display.width", 250)
    print(res.round(4).to_string(index=False))
    print(camp[["combines_at_once", "reading", "denial_p", "e_combine", "e_funded", "median_log_growth",
                "ruin_probability", "median_days_to_first_payout", "mean_max_drawdown"]].round(4).to_string(index=False))
    print(f"VERDICT ({c['prereg_id']}): {verdict} -- resolution {'met' if rule1 else 'NOT met'}, gate "
          f"{'passed' if rule2 else 'NOT passed'}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--workers", type=int, default=4)
    raise SystemExit(main(workers=ap.parse_args().workers))
