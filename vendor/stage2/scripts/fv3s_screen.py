"""EXPLORATORY (D-407): FV3-S's cheap screen rerun once, under the operator's ruling that D-406's environment was a
specification failure (D-307's rule) -- the same three exported tables (versions 19, 20 and 21, their policies files
checked against the solves' manifests), the same binary campaign check, seed and kill line as D-405 (5), with D-406
(3)'s reading of the growth floor; the one correction: the check's bankroll is an output of the run, as FV3's gate
reads a campaign (D-312: cash that never binds; the growth and the measures on the required bankroll at p90).

    python scripts/fv3s_screen.py

At each of the two solved cells, each version's table and v12's (`results/state_policy_v12_policies.json`) through
`state_policy_dp.campaign` under the corrected check; the lines at -0.05 (FV3-C's development cell) decide, -0.025
beside: a version passes when its mean red-month share AND its mean monthly spread are below v12's and its median
growth on the required bankroll is at least v12's less a fifth of its size. CONTINUE when any version passes; KILL
otherwise -- and a kill closes FV3-S (D-407 (5)).

Writes results/fv3s_screen.csv (`check`, `line`, `verdict` rows) with its manifest; the runs recorded under
`D-407:fv3s_screen`.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

SCRIPT = "scripts/fv3s_screen.py"
DECISION = "D-407"
VERSIONS = {19: 50.0, 20: 150.0, 21: 350.0}         # D-405 (2): the coin's loss per version
CELLS = (-0.05, -0.025)
DECIDING_CELL = -0.05                                # FV3-C's development cell (D-405 (5))
REFERENCE = "results/state_policy_v12_policies.json"
COLS = ("pf_growth_on_base_p50", "pf_required_p90", "st_red_share_mean", "st_red_share_p50", "st_month_sd_mean",
        "st_month_sd_p50", "st_month_median_mean", "st_worst_month_p05", "st_best_month_p50", "st_best_month_p95",
        "st_payouts_per_month_mean", "st_underwater_days_p50", "st_max_drawdown_p95", "median_days_to_first_payout",
        "share_accounts_ever_paid", "ruin_probability", "xfa_mean_days", "xfa_share_paid")


def policies_sha(path: Path) -> str:
    """The policies file's sha256 as the solver hashed it (its payload with LF line ends)."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def same_tables_problems(rd: Path) -> list[str]:
    """D-407: each version's policies file must be the one its solve recorded (the manifest's notes)."""
    out = []
    for v in VERSIONS:
        m = json.loads((rd / f"state_policy_v{v}.csv.manifest.json").read_text(encoding="utf-8"))
        want = (m.get("notes") or {}).get("policies_json_sha256")
        got = policies_sha(rd / f"state_policy_v{v}_policies.json")
        if want != got:
            out.append(f"state_policy_v{v}_policies.json is not the table its solve recorded ({got[:12]} != {str(want)[:12]})")
    return out


def lines(version: dict, reference: dict) -> dict:
    """D-405 (5)'s three lines with D-406 (3)'s growth floor: (red below, spread below, floor met, all three)."""
    g, g0 = float(version["pf_growth_on_base_p50"]), float(reference["pf_growth_on_base_p50"])
    red = float(version["st_red_share_mean"]) < float(reference["st_red_share_mean"])
    sd = float(version["st_month_sd_mean"]) < float(reference["st_month_sd_mean"])
    floor = g >= g0 - 0.2 * abs(g0)
    return {"red_below": bool(red), "spread_below": bool(sd), "growth_floor": bool(floor), "passes": bool(red and sd and floor)}


def verdict(line_rows: list[dict]) -> str:
    """CONTINUE when any version passes at the deciding cell, else KILL."""
    return "continue" if any(r["passes"] for r in line_rows if abs(r["edge"] - DECIDING_CELL) < 1e-9) else "kill"


def corrected_check(cfg: dict) -> dict:
    """D-407's one correction: the campaign check with its bankroll an output (`bankroll_mode: output`)."""
    out = dict(cfg)
    out["campaign_check"] = {**cfg["campaign_check"], "bankroll_mode": "output"}
    return out


def main(argv: list[str] | None = None, *, results_dir: Path | None = None, workers: int = 4) -> int:
    from multiprocessing import Pool

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.payout_method import rules_for_method
    from propedge.reporting.results import write_result

    import state_policy_dp as dp

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    bad = same_tables_problems(rd)
    if bad:
        print("REFUSED (D-407): " + "; ".join(bad))
        return 2
    ref = json.loads((rd / Path(REFERENCE).name).read_text(encoding="utf-8"))
    jobs, meta = [], []
    for v in VERSIONS:
        cfg = corrected_check(dp.config(dp.config_for(v)))
        rules = rules_for_method(cfg["campaign_check"]["payout_method"])
        pol = json.loads((rd / f"state_policy_v{v}_policies.json").read_text(encoding="utf-8"))
        seed = int(cfg["campaign_check"]["seed"])
        for e in CELLS:
            pid = f"state_dp_e{e:+.3f}_lamstar"
            jobs.append((cfg, rules, e, None, f"v{v}:{pid}", pol[pid], seed, results_dir))
            meta.append((v, e, "version"))
            if v == min(VERSIONS):                       # v12's table once per cell (the same check for every version)
                jobs.append((cfg, rules, e, None, f"v12:{pid}", ref[pid], seed, results_dir))
                meta.append((12, e, "reference"))
    with Pool(min(int(workers), len(jobs))) as pool:
        done = pool.map(dp._campaign_job, jobs)
    rows = []
    for (v, e, kind), r in zip(meta, done):
        rows.append({"section": "check", "version": v, "coin_loss": VERSIONS.get(v, 0.0), "edge": e, "kind": kind,
                     "policy_id": r["policy_id"], **{k: r.get(k) for k in COLS}})
        print(f"check v{v} e={e:+.3f}: growth on base {r.get('pf_growth_on_base_p50'):.4f}, red {r.get('st_red_share_mean'):.4f}, "
              f"spread {r.get('st_month_sd_mean'):.1f}, ruin {r.get('ruin_probability'):.3f}", flush=True)
    chk = pd.DataFrame(rows)
    line_rows = []
    for v in VERSIONS:
        for e in CELLS:
            me = chk[(chk["version"] == v) & (chk["edge"] == e)].iloc[0]
            r0 = chk[(chk["version"] == 12) & (chk["edge"] == e)].iloc[0]
            line_rows.append({"section": "line", "version": v, "coin_loss": VERSIONS[v], "edge": e,
                              "deciding": abs(e - DECIDING_CELL) < 1e-9, **lines(me, r0)})
    vd = verdict(line_rows)
    out = pd.concat([chk, pd.DataFrame(line_rows),
                     pd.DataFrame([{"section": "verdict", "verdict": vd, "edge": DECIDING_CELL,
                                    "passing_versions": ",".join(str(r["version"]) for r in line_rows
                                                                 if r["passes"] and r["deciding"])}])], ignore_index=True)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for v in VERSIONS:
        for e in CELLS:
            counter.record(prereg_id=f"{DECISION}:fv3s_screen", seed=20261016, exploratory=True,
                           params={"study": "FV3-S screen, corrected", "export_version": v, "coin_loss": VERSIONS[v],
                                   "edge": e, "bankroll_mode": "output"},
                           label=f"FV3-S's screen rerun (D-407): table v{v} at e={e:+.3f}, the bankroll an output")
    write_result(out, "fv3s_screen", script=SCRIPT, seed=20261016, exploratory=True, results_dir=results_dir,
                 parameters={"decision": DECISION, "versions": {str(k): v for k, v in VERSIONS.items()},
                             "cells": list(CELLS), "deciding_cell": DECIDING_CELL, "reference": REFERENCE,
                             "correction": "campaign_check.bankroll_mode output (D-312's never-binding cash)",
                             "kill_line": "red-month share and monthly spread (means) below v12's, growth on the required "
                                          "bankroll at least v12's less a fifth of its size (D-405 (5), D-406 (3))",
                             "sources": [f"results/state_policy_v{v}.csv" for v in VERSIONS]},
                 notes={"status": "EXPLORATORY: FV3-S's cheap screen, the single corrected rerun (D-307's rule, D-407)"},
                 description="EXPLORATORY: FV3-S's cheap screen rerun once with the check's bankroll an output (D-407): "
                             "each penalised table and v12's through the binary campaign check at the two solved cells, "
                             "the kill line's three lines per version, and the verdict at FV3-C's cell.")
    print(f"VERDICT (D-407): {vd.upper()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
