"""EXPLORATORY, viewing only (D-392): D-390's SPEED version -- the after-win lever at 1, the 08:30 2x collect bracket
every trading day after the big win -- over every development day of FV3-C's Studio run, with its per-path record and
the Studio's mirror spec, so the operator can look at its accounts in the Studio (the operator, 2026-10-18: "please
have the studio updated with the full runs so I can review the overview of the accounts with the flip days that
decreased time to payout"). No verdict is read from it: D-391's stands. D-395 (6): a SPEED-2 setting the same way.

    python scripts/fv3d_after_win_studio.py                                   # D-392: SPEED (after_win = 1)
    python scripts/fv3d_after_win_studio.py --lever speed_first --value N     # D-395 (6): SPEED-2's setting N

* **The campaign:** FV3-C's (`config/fv3_corrected_portfolio.yaml`) with the lever at its value, on the identity
  period's trades and days (every development day, the development scorer's yearly bound) -- the run the lever
  harness's identity reproduces as `fv3_corrected_v1` at 0 -- the collect stream priced on those days' years (D-390
  (3)). The days and the trades per day are checked equal to the Studio's FV3-C export (`fv3_studio_corrected_v1_*`)
  before anything runs, so the Studio replays the logs it already holds.
* **The mirror, per arm:** FV3-C's exported mirror with four keys changed -- `risk_policy` (FV3-C's cell with the
  after-win layer, which `RiskPolicy.from_dict` rebuilds whole, D-392), `policy_id`, `flip` and `reproduces` -- plus
  `logs`, the files it replays. SPEED's `flip` is the 2x collect bracket as one `FlipSpec` (the only bracket that layer
  takes -- FV3-C's table takes no flip of its own, its mirror's flip is null); SPEED-2's is the collect menu
  (`FlipMenu.as_dict()`: the layer picks a bracket per state). Each at its Wilson bound on the verdict arm, as the gate
  ran it.

Writes results/fv3d_after_win_speed_full.csv (SPEED) or results/fv3d_speed_first_<post>_full.csv (SPEED-2) -- laid
out as a grid's gate section (`section` "gate", keyed by shift, enforcement_p and placement; every scalar column the
gate returns), both arms at 0 and 10 % denial, the mirrors in its manifest's `parameters.mirror` -- and its _paths.csv
(D-310's per-path layout, the run labelled "gate placement off" as the scorer labels it). Counted under
`D-390:fv3d_levers` or `D-395:fv3d_levers`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import pandas as pd  # noqa: E402

import fv3d_lever_test as lt  # noqa: E402

SCRIPT = "scripts/fv3d_after_win_studio.py"
RESULT = "fv3d_after_win_speed_full"
VALUE = 1                                            # D-390: the lever's SPEED setting
LABEL = "gate placement off"                         # the scorer's label for the gate's run (D-310)
LOGS = {"point": "fv3_studio_corrected_v1_point_trades", "verdict": "fv3_studio_corrected_v1_verdict_trades"}
DAYS_FILE = "fv3_studio_corrected_v1_days"
SHIFT = {"point": "point", "verdict": "lower_bound"}
#: the run's decision, the lever's decision and the variant family, by lever
DECISIONS = {"after_win": ("D-392", "D-390"), "speed_first": ("D-395 (6)", "D-395")}


def result_name(lever: str, value: int) -> str:
    if lever == "after_win" and int(value) == VALUE:
        return RESULT
    if lever == "speed_first" and int(value) in lt.SPEED_FIRST:
        return f"fv3d_speed_first_{lt.SPEED_FIRST[int(value)]}_full"
    raise ValueError(f"no Studio run is declared for {lever} = {value} (D-392, D-395 (6))")


def mirror_for(fv3c: dict, policy, flip, arm: str, result: str = RESULT) -> dict:
    """FV3-C's exported mirror for `arm` with the after-win layer and its flip stream (one bracket or the menu);
    refuses a mirror that is not FV3-C's cell or already carries a flip stream."""
    if fv3c.get("policy_id") != policy.base.id:
        raise SystemExit(f"REFUSED: the Studio's FV3-C mirror runs {fv3c.get('policy_id')}, the run {policy.base.id}.")
    if fv3c.get("flip") is not None:
        raise SystemExit("REFUSED: the Studio's FV3-C mirror carries a flip stream; the layer's bracket would replace it.")
    spec = flip if arm == "point" else flip.at_lower_bound()
    return {**fv3c, "risk_policy": policy.as_dict(), "policy_id": policy.id, "flip": spec.as_dict(),
            "reproduces": f"results/{result}.csv, section gate, shift {SHIFT[arm]}, enforcement_p 0, placement off",
            "logs": {"trades": f"results/{LOGS[arm]}.csv", "days": f"results/{DAYS_FILE}.csv"}}


def check_logs(rd: Path, tp: pd.DataFrame, dp: list[str]) -> None:
    """The Studio's FV3-C export holds the same days and the same trades per day as the run."""
    from propedge.reporting.results import read_result

    ds = read_result(rd / f"{DAYS_FILE}.csv")
    if [str(d)[:10] for d in ds["date"]] != [str(d)[:10] for d in dp]:
        raise SystemExit("REFUSED: the Studio's day set is not the run's days.")
    per_day = tp.groupby(tp["date"].astype(str).str[:10]).size()
    want = pd.Series(ds["entries"].astype(int).values, index=[str(d)[:10] for d in ds["date"]])
    if not want.reindex(per_day.index).fillna(-1).astype(int).equals(per_day.astype(int)) or int(want.sum()) != len(tp):
        raise SystemExit("REFUSED: the Studio's day set counts other trades per day than the run's.")
    for arm, name in LOGS.items():
        if len(read_result(rd / f"{name}.csv")) != len(tp):
            raise SystemExit(f"REFUSED: the Studio's {arm} log holds another number of trades than the run's.")


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.campaign.after_win import AfterWinPolicy, brackets_of
    from propedge.campaign.risk_policy import RiskPolicy
    from propedge.reporting.results import write_result

    import fv3_xfa_time_budget as xb
    import score_fv3_grid as gf

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--lever", choices=tuple(DECISIONS), default="after_win")
    ap.add_argument("--value", type=int, default=VALUE)
    a = ap.parse_args(argv)
    lever, value = a.lever, int(a.value)
    result = result_name(lever, value)
    decision, lever_decision = DECISIONS[lever]

    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    cfg = gf.config(lt.CONFIG)
    print("rebuilding the development trades...")
    t, days, tv = xb.rebuild_trades(cfg)
    tp, dp = lt.in_period(t, days, *lt.PERIODS["identity"])
    check_logs(rd, tp, dp)

    # the policy and the flip stream as run_one builds them
    c = lt.configure(cfg, lever, value, sorted({int(str(d)[:4]) for d in dp}))
    stats = lt.period_stats(tp, dp, [float(R) for R in gf.rr_menu(c)], "yearly")
    fr = float(c["state_policy"]["fresh"]["funded_rr"])
    base, e_used, _ = gf.policy_for_edge(c, stats[fr]["lb"])
    menu = gf.flip_spec_of(c)
    if lever == "speed_first":
        policy = AfterWinPolicy.over(base, "speed_first", post_payout=lt.SPEED_FIRST[value], brackets=brackets_of(menu))
        flip = menu                                  # D-395 (6): the layer picks a bracket per state
    else:
        policy = AfterWinPolicy.over(base, lt.AFTER_WIN[value])
        flip = menu.spec_for(policy.flip_risk, policy.flip_rr)   # D-392: the one bracket SPEED takes
    rebuilt = RiskPolicy.from_dict(json.loads(json.dumps(policy.as_dict())))
    if not isinstance(rebuilt, AfterWinPolicy) or rebuilt.as_dict() != policy.as_dict():
        raise SystemExit("REFUSED: the after-win policy does not survive its dict (D-392).")

    print(f"identity: {lever} = {value} ({len(tp)} trades over {len(dp)} days)...")
    paths_rows: list[dict] = []
    df = lt.run_one(cfg, value, tp, dp, tv, "yearly", lever, sink=paths_rows, label=LABEL)
    if set(df["policy_id"].astype(str)) != {policy.id}:
        raise SystemExit(f"REFUSED: the run's policy is {set(df['policy_id'])}, the mirror's {policy.id}.")
    mirror = {}
    for arm, name in LOGS.items():
        fv3c = json.loads((rd / f"{name}.csv.manifest.json").read_text(encoding="utf-8"))["parameters"]["mirror"]
        mirror[arm] = mirror_for(fv3c, policy, flip, arm, result)
        if abs(float(fv3c["policy_edge"]) - float(e_used)) > 1e-12:
            raise SystemExit(f"REFUSED: the run's table cell is at edge {e_used}, the Studio's FV3-C at {fv3c['policy_edge']}.")
        if int(fv3c["seed"]) != int(cfg["seeds"]["gate"]):
            raise SystemExit(f"REFUSED: the Studio's FV3-C mirror seeds {fv3c['seed']}, the run {cfg['seeds']['gate']}.")

    counter = VariantCounter(path=rd / "variants.jsonl")
    seed = int(cfg["seeds"]["gate"])
    counter.record(prereg_id=f"{lever_decision}:fv3d_levers", seed=seed, exploratory=True,
                   params={"lever": lever, "value": value, "period": "identity", "bound_rule": "yearly",
                           "config": "config/fv3_corrected_portfolio.yaml", "decision": decision},
                   label=f"FV3-D lever test: {lever} = {value}, identity, for the Studio ({decision}, viewing only)")
    n_var = len({r["variant_id"] for r in counter.all() if str(r.get("prereg_id", "")).endswith(":fv3d_levers")})
    # a grid's gate section: every scalar column the gate returns, keyed as the scorer keys it
    scalar = [k for k in df.columns if not df[k].map(lambda v: isinstance(v, (list, dict, tuple))).any()]
    res = df[scalar].copy()
    res.insert(0, "section", "gate")
    status = ("EXPLORATORY, viewing only: no verdict is read from it (D-391's stands)" if lever == "after_win" else
              "EXPLORATORY, viewing only: no verdict is read from it (D-395's walk-forward is the test)")
    what = ("D-390's SPEED layer (the 08:30 2x collect bracket every trading day after the big win)" if lever == "after_win"
            else f"D-395's SPEED-2 layer (the collect brackets until the account can request; after a payout the "
                 f"{lt.SPEED_FIRST[value]})")
    write_result(res, result, script=SCRIPT, seed=seed, exploratory=True, results_dir=results_dir, variant_count=n_var,
                 parameters={"lever": lever, "value": value, "period": "identity", "range": [dp[0], dp[-1]],
                             "bound_rule": "yearly", "levels": list(lt.LEVELS), "config": "config/fv3_corrected_portfolio.yaml",
                             "decision": decision, "lever_decision": lever_decision, "paths_file": f"{result}_paths.csv",
                             "bracket": flip.as_dict(), "mirror": mirror},
                 notes={"status": status},
                 description=f"EXPLORATORY, viewing only ({decision}): FV3-C with {what} over every development day, both "
                             "arms at 0 and 10 % denial, with the Studio's mirror spec per arm.")
    write_result(pd.DataFrame(paths_rows), f"{result}_paths", script=SCRIPT, seed=seed, exploratory=True,
                 results_dir=results_dir, variant_count=n_var,
                 parameters={"result": f"{result}.csv", "decision": decision, "config": "config/fv3_corrected_portfolio.yaml",
                             "measures": "propedge.campaign.portfolio.path_measures on the run's capital base, one row per "
                                         "resampled path of each arm and denial level (`run`, `shift`, `enforcement_p`)"},
                 notes={"status": status, "companion_of": f"{result}.csv"},
                 description=f"The per-path record of {result}.csv (D-310's form), so the Studio's replay can be checked "
                             "path by path.")
    pd.set_option("display.width", 220)
    print(res.dropna(axis=1, how="all").round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
