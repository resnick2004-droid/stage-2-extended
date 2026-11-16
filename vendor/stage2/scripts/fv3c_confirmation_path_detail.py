"""P-06's gate campaign re-run with every path's record (R1, D-457; EXPLORATORY, never the verdict).

    python scripts/fv3c_confirmation_path_detail.py

FV3-C's confirmation file (`results/fv3_confirmation.csv`, P-06) was written before the steadiness measures existed
(D-402), and its per-path companion (`results/fv3_confirmation_paths.csv`) holds one row of totals per path, not each
path's cash by day. The success criteria's FLAG levels (`docs/SUCCESS_CRITERIA.md` §5) need both, so this script
re-runs the two arms the levels read -- the gate's placement off at 0 % denial, at the lower bound and at the point --
exactly as `scripts/confirm_fv3.py` ran them: the same frozen candidate, the same ingested captures of the held-back
window (read once by P-06; nothing new is read), the same blocks, policy, seed and campaign, one level instead of the
ladder (the gate runs every arm on common random numbers from one seed, so the arms' paths do not depend on which
other arms run).

**The identity, before any measure is kept:** every path's totals from this run (final cash, fees, payouts, the
deepest loss from the start, the largest drawdown, the days to the first payout, the trades) must equal P-06's saved
paths exactly, arm for arm and path for path; a difference refuses the run and writes nothing.

Then, per path and arm: the steadiness measures (`propedge.campaign.steadiness.path_steadiness`, D-402), the payouts
that arrived, the Combines bought, passed and the days each pass took, the funded accounts and their gross payouts.
Writes `results/fv3c_confirmation_path_detail.csv` with its manifest (exploratory, P-06's seed).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/fv3c_confirmation_path_detail.py"
RESULT = "fv3c_confirmation_path_detail"
SAVED_PATHS = "fv3_confirmation_paths.csv"
ARM_RUN = "gate placement off"
#: the saved per-path columns the identity compares, exactly
IDENTITY = ("final_cash", "fees", "payouts", "deepest_loss_from_start", "max_drawdown", "days_to_first_payout",
            "trades", "combine_attempts", "xfas")


def path_detail(x: Any) -> dict[str, float]:
    """One path's record: steadiness, payouts that arrived, Combines and funded accounts (a `LockstepPath`)."""
    from propedge.campaign import steadiness as st

    p = x.path
    n_pay = st.payouts_arrived(p)
    out: dict[str, float] = {f"st_{k}": v for k, v in st.path_steadiness(p.cash_series, p.initial_bankroll,
                                                                           n_pay).items()}
    combines = tuple(x.combines)
    passed = [c for c in combines if c.passed]
    funded = tuple(x.funded)
    gross = float(sum(a.gross_paid for a in funded))
    n_paid = int(sum(a.n_payouts for a in funded))
    out.update({
        "payouts_arrived": float(n_pay),
        "combines_bought": float(len(combines)),
        "combines_passed": float(len(passed)),
        "combine_pass_share": float(len(passed)) / len(combines) if combines else float("nan"),
        "days_to_pass_median": float(np.median([c.pass_day - c.purchase_day for c in passed])) if passed
        else float("nan"),
        "funded_accounts": float(len(funded)),
        "gross_paid": gross,
        "payouts_requested": float(n_paid),
        "mean_gross_payout": gross / n_paid if n_paid else float("nan"),
    })
    return out


def main(argv: list[str] | None = None) -> int:
    import confirm_fv3 as cf
    import portfolio_stage as ps
    import score_fv3_grid as gf
    from propedge import RESULTS_DIR
    from propedge.campaign import gate
    from propedge.campaign.payout_method import rules_for_method
    from propedge.campaign.protocols import Protocol
    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel
    from propedge.reporting.results import read_result, write_result
    from propedge.research.model_card import BAND_FILE, setups_minimum

    rd, rund = RESULTS_DIR, ROOT / "runs"
    conf = cf.config()
    states = {str(p["id"]): cf.period_state(p, rd, rund) for p in conf["periods"]}
    chosen = {k: run for k, (s, run, _) in states.items() if s == "ingested"}
    cand = cf.candidate(conf)
    sig, ses, bench, sessions_by, window_days, label_of_day = cf.load_window(conf, cand, chosen, rd, rund)
    fm = FillModel.load("assumed")
    q = params("NQ")
    tv = q["micro_tick"] * q["micro_point_value"]
    S = gf.Signals3(sig, float(fm.round_turn_by_instrument[q["micro"]]), float(fm.round_turn_by_instrument["NQ"]), tv,
                    cand["ladder"])
    S.year = np.array([label_of_day[str(d)] for d in S.df["date"]], dtype=int)
    fresh = cand["state_policy"]["fresh"]
    need = setups_minimum(float(fresh["combine_rr"]), float(fresh["combine_risk"]), 0.0)
    ev = gf.EvaluatedFV3(S, ses, cand, sessions_by, read_result(BAND_FILE), float(need))
    final = ev.cells[0]
    t = gf.gate_trades(S, ev, {int(y): 0 for y in ev.years}, final)
    menu = [float(R) for R in gf.rr_menu(cand)]
    n_trials = None if str(conf.get("ledger_n", "pending")).lower() == "pending" else int(conf["ledger_n"])
    stats = cf.edge_stats(t, menu, window_days, int(conf["block_days"]), n_trials)
    seed = int(cand["seeds"]["gate"])
    fr = float(fresh["funded_rr"])
    blocks, n_used = gf.gate_blocks(t, window_days, tv, menu, require_sides=True, require_exits=True)
    if n_used != len(t):
        print("REFUSED: the blocks hold a different number of trades.")
        return 2
    policy, _, _ = gf.policy_for_edge(cand, stats[fr]["lb"])

    sink: list[dict] = []
    details: list[dict] = []
    base_hook = ps.composed_hook(cand["portfolio"], sink=sink)

    def hook(shift: str, p: float, paths) -> dict:
        out = base_hook(shift, p, paths)
        for i, x in enumerate(paths):
            details.append({"shift": shift, "enforcement_p": float(p), "path": i, **path_detail(x)})
        return out
    hook.state = base_hook.state                                       # the sink labels each run, as P-06's did
    hook.state["label"] = ARM_RUN

    # gf.run_gate's placement-off call, its arguments unchanged, at 0 % denial only
    camp = cand["gate"]["campaign"]
    protocol = Protocol(name="fv3", combine_rr=float(fresh["combine_rr"]), combine_risk=float(fresh["combine_risk"]),
                        funded_rr=float(fresh["funded_rr"]), funded_risk=float(fresh["funded_risk"]),
                        trades_per_day=gf.MAX_PER_DAY, payout_path="standard", keep_balance=0.0, payout_frac=1.0,
                        max_concurrent_accounts=int(camp["accounts"]), family="fv3", source="config/fv3_grid.yaml",
                        note="FV3's gate under the state policy (D-290)", params=gf.protocol_params(cand))
    if bool(camp["rtp"]):
        print("REFUSED: the frozen candidate's base case is not placement off.")
        return 2
    e_by = {R: stats[R]["e"] for R in menu}
    lb_by = {R: stats[R]["lb"] for R in menu}
    gate.run_gate(
        blocks, e=e_by[fr], lb=lb_by[fr], protocol=protocol, bankroll=gf.bankroll_of(cand),
        horizon_days=int(camp["horizon_days"]), n_paths=int(camp["n_paths"]), seed=seed, accounts=int(camp["accounts"]),
        sizing=gf.sizing_rule(cand, tv), rules=rules_for_method(camp["payout_method"]), mode=camp["mode"],
        settlement=camp["settlement"], combines=int(camp["combines"]), total_accounts=int(camp["accounts"]),
        risk_policy=policy, e_by_rr=e_by, lb_by_rr=lb_by, rtp=False, path_hook=hook,
        routing=gf.fidelity_of(cand)["routing"],
        cross_account=bool(gf.fidelity_of(cand).get("cross_account_rule", False)),
        flip=gf.flip_spec_of(cand), hold_to_own_exit=bool(gf.fidelity_of(cand).get("hold_to_own_exit", False)),
        levels=(0.0,))

    # the identity: this run's per-path totals against P-06's saved paths, exactly
    read_result(rd / SAVED_PATHS)                         # the manifest's sha256 checked first
    # read exactly: pandas' default float parser can miss the written value by an ulp, which would fail an exact
    # comparison for nothing (the first run of this script did; D-471)
    saved = pd.read_csv(rd / SAVED_PATHS, float_precision="round_trip", low_memory=False)
    saved = saved[(saved["run"] == ARM_RUN) & (saved["enforcement_p"].astype(float) == 0.0)]
    mine = pd.DataFrame(sink)
    bad = []
    for shift in ("lower_bound", "point"):
        a = saved[saved["shift"] == shift].sort_values("path").reset_index(drop=True)
        b = mine[(mine["shift"] == shift) & (mine["enforcement_p"].astype(float) == 0.0)].sort_values("path")
        b = b.reset_index(drop=True)
        if len(a) != len(b) or not len(a):
            bad.append(f"{shift}: {len(b)} paths against {len(a)} saved")
            continue
        for col in IDENTITY:
            x = pd.to_numeric(a[col], errors="coerce").to_numpy(float)
            y = pd.to_numeric(b[col], errors="coerce").to_numpy(float)
            same = np.array_equal(np.nan_to_num(x, nan=-1e300), np.nan_to_num(y, nan=-1e300))
            if not same:
                k = int(np.sum(~np.isclose(x, y, equal_nan=True, rtol=0, atol=0)))
                bad.append(f"{shift} {col}: {k} paths differ")
    if bad:
        print("REFUSED: the re-run does not reproduce P-06's saved paths -- " + "; ".join(bad))
        return 3
    det = pd.DataFrame(details)
    out = mine.merge(det, on=["shift", "enforcement_p", "path"], how="inner", validate="one_to_one")
    write_result(out, RESULT, script=SCRIPT, seed=seed, exploratory=True,
                 parameters={"source_verdict": "results/fv3_confirmation.csv", "source_paths": f"results/{SAVED_PATHS}",
                             "arms": [f"{ARM_RUN}, lower_bound, 0 %", f"{ARM_RUN}, point, 0 %"],
                             "identity_columns": list(IDENTITY), "identity": "exact, every path of both arms",
                             "periods": chosen},
                 description="P-06's gate campaign (placement off, 0 % denial, both shifts) re-run with each path's "
                             "record, after reproducing the saved paths exactly; the steadiness measures, payouts that "
                             "arrived, Combine passes and gross payouts per path. EXPLORATORY: for the FLAG levels of "
                             "docs/SUCCESS_CRITERIA.md; never the verdict, which stands as P-06 recorded it.",
                 notes={"status": "EXPLORATORY measurement on a read window (R1, D-457)", "prereg_of_source": "P-06"})
    print(f"identity exact on {len(out)} paths; wrote results/{RESULT}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
