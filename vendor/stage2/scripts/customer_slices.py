"""EXPLORATORY (D-508): the customer-experience ("slice") study -- what a user who starts on any day of the development
window sees over their first 21, 63 and 126 trading days -- on the leading configurations. Read beside, never a gate.

    python scripts/customer_slices.py --check              # the Studio identity only (P-13's full-window replays)
    python scripts/customer_slices.py --workers 6          # the study: every start, every horizon, every configuration

**The slice.** For every trading day of a configuration's development window as a start (fresh bankroll, fresh
accounts), the campaign runs forward on that configuration's trades **in their historical order** -- no resampling: the
engine's as-happened replay (`SharedDayDraws(replay=True)`, D-130), the same day sequence the Campaign Studio's replay
steps through -- for 21, 63 and 126 trading days (a start too late for a horizon is skipped for that horizon). Campaign
day 0 is the purchase evening before the start's session; day k closes the start's k-th session. Each configuration
keeps its own protocol exactly as its registered (or compliance) run handed it to `gate.run_gate` -- every switch,
the strict one-at-a-time rule where that run had it (P-13's five minutes; FV3-C none), its table, its purchase budget,
the placement off (D-289), 0 % denial (D-234) -- and its outcomes at the arm named (`verdict`: every R shifted to the
bound the gate read, `gate.shifted_blocks`, as the gate row; `point`: as traded). The bankroll never binds (the gate's
`UNBOUND_BANKROLL`, as the Studio's unconstrained run): what a customer needs is read off the slice's own cash.

==================  =====  =================================================  ==========================
config              arm    trades and protocol                                table, purchase budget
==================  =====  =================================================  ==========================
p13                 verdict P-13's campaign (A3-BRK30, D-500)                 v12, none
p13                 point   the same, outcomes as traded                      v12, none
p13_noclose         verdict P-13's campaign                                   no-closure (D-502), none
p13_noclose_b20     verdict P-13's campaign                                   no-closure, 20 in 21 days
p13_noclose_b30     verdict P-13's campaign                                   no-closure, 30 in 21 days
fv3c                verdict FV3-C's development campaign (D-505's)            v12, none
fv3c_noclose_b20    verdict FV3-C's development campaign                      no-closure, 20 in 21 days
==================  =====  =================================================  ==========================

**First, the identity (refused otherwise):** P-13's full-window replay through this script's engine call -- every
session of the window from day 0, once, at both arms -- must equal the Studio's P-13 mirror replays
(`<studio store>/runs/*a3_brk30_p13_mirror_-_verdict*` and `*_-_point*`): campaign cash by day (the Studio's
`replay_cash.csv`, re-based to its bankroll and rounded to the cent) to the cent, and the path's fees, payouts,
attempts, funded accounts and first-payout day (its `payload.json`) exactly (dollar totals to 1e-6: the Studio reads
its outcomes back from a CSV, so a sum may differ in its last bits). So the engine and its state at day 0 are
the Studio's.

**Per slice** (section `slice`): the net cash at the end (`end_net`; payouts received less every fee paid; a payout
requested but not yet arrived is not cash), whether it ends positive, the Combine passes and the payouts received
(count and dollars), whether none, the trading days to the first pass and the first payout, the longest stretch of
trading days without a pass and without a payout (from the start, between events, to the end: a slice without one is
its whole horizon), the deepest drawdown from the start (the cash below the starting bankroll) and from a running high,
and the bankroll it needed (`needed_bankroll` = the drawdown from the start plus one Combine subscription, the
Studio's margin). **Per configuration x arm x horizon** (section `summary`): the share of slices positive, the net's
5th / 10th percentile, median, 90th percentile and worst, the passes' and payouts' 10th percentile and median, the share
with no pass and with no payout, the longest gaps' 90th percentile and the needed bankroll's 95th percentile (the
bankroll a customer needs so the 95th-percentile slice drawdown never forces them out). Percentiles are numpy's linear.

Written: `results/customer_slices.csv` (sections `slice` and `summary`, the schema agreed with the Studio's builder;
columns that do not apply blank); the identity's record in its manifest (`parameters.studio_identity`). EXPLORATORY: the seven readings
recorded in `results/variants.jsonl` under `D-508:customer_slices`. Read beside, never a gate (D-234); a protocol ranked
on these readings is a new candidate with its own pre-registration (D-508 (5)).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __name__ == "__main__":                 # one BLAS thread, before numpy loads (D-464 (5))
    for _k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(_k, "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SCRIPT = "scripts/customer_slices.py"
DECISION = "D-508"
RESULT = "customer_slices"
FAMILY_ID = f"{DECISION}:customer_slices"
HORIZONS = (21, 63, 126)
BUDGET_WINDOW = 21
#: the funded account's horizon in a replay: "never" -- it lives as long as the log (the Studio's replay, D-130)
FUNDED_HORIZON = 100_000
COMBINE_MAX_DAYS = 2000
STUDIO_STORE = Path("C:/Users/resni/OneDrive/Desktop/Stage 2C - Campaign Studio/store")
STUDIO_RUNS = {"verdict": "*a3_brk30_p13_mirror_-_verdict*", "point": "*a3_brk30_p13_mirror_-_point*"}
#: the Studio path's totals that must equal ours exactly (payload.json's replay path)
STUDIO_PATH_KEYS = ("total_fees", "total_payouts", "attempts_started", "accounts_funded", "accounts_ever_paid",
                    "days_to_first_payout", "trades_sized", "funded_abandoned")
#: the totals' tolerance in dollars: the Studio reads its outcomes back from a CSV, so a sum may differ in its last bits
#: (D-507 saw one unit in the sixteenth digit); counts and days are integers and must be equal
TOTAL_TOL = 1e-6
READING = "EXPLORATORY (D-508): beside the verdicts, never a gate (D-234)"
WORKER_MEMORY_GB = 0.5                    # one slice worker's resident memory, rounded up (the guard's divisor)

#: the configurations (D-508 (2)) -- (config, arm, campaign, table, purchase budget)
CONFIGS = (
    ("p13", "verdict", "p13", "v12", None),
    ("p13", "point", "p13", "v12", None),
    ("p13_noclose", "verdict", "p13", "noclose", None),
    ("p13_noclose_b20", "verdict", "p13", "noclose", (20, BUDGET_WINDOW)),
    ("p13_noclose_b30", "verdict", "p13", "noclose", (30, BUDGET_WINDOW)),
    ("fv3c", "verdict", "fv3c", "v12", None),
    ("fv3c_noclose_b20", "verdict", "fv3c", "noclose", (20, BUDGET_WINDOW)),
)
SLICE_COLS = ("section", "config", "arm", "horizon", "start_day", "start_date", "end_net", "positive", "passes",
              "payouts", "payout_dollars", "no_pass", "no_payout", "days_to_first_pass", "days_to_first_payout",
              "longest_pass_gap", "longest_payout_gap", "drawdown_from_start", "drawdown_from_high", "needed_bankroll")
SUMMARY_COLS = ("n_slices", "share_positive", "net_p5", "net_p10", "net_median", "net_p90", "net_worst", "passes_p10",
                "passes_median", "payouts_p10", "payouts_median", "share_no_pass", "share_no_payout",
                "longest_pass_gap_p90", "longest_payout_gap_p90", "needed_bankroll_p95")


# ------------------------------------------------------------------------------------------------ the campaigns


@dataclass
class Campaign:
    """One campaign's trades and protocol: its blocks (point), the session dates, and `gate.run_gate`'s arguments
    (all but `blocks`, `path_hook`, `n_paths`, `purchase_budget`) exactly as its registered run passed them."""
    name: str
    blocks: list
    dates: list
    kw: dict


def p13_campaign() -> Campaign:
    """P-13's campaign as `a3_compliance.study` builds it (= `a3_brk30`'s registered run): the cell's trades from the A3
    rung cache, the blocks, the 0.05 bounds by the screen's era rule, the day capacity, FV3-C's v12 policy, the strict
    rule, P-13's seed; `atlas_a3.gate_kwargs` (the placement off, 0 %)."""
    import a3_brk30 as B
    import a3_compliance as a3
    import atlas_a3 as A

    L = B.inputs()
    t, days = B.cell_trades(L)
    ci = a3.campaign_inputs(L, t, days)
    horizon = int(L["fcfg"]["gate"]["campaign"]["horizon_days"])
    kw = A.gate_kwargs(ci["blocks"], L["fcfg"], float(L["tv"]), ci["policy"], ci["e_by"], ci["lb_by"], None,
                       seed=B.SEED, n_paths=1, horizon=horizon, capacity=ci["cap"], levels=(0.0,), rtp=False,
                       one_at_a_time=B.STRICT_GAP)
    blocks = kw.pop("blocks")
    kw.pop("path_hook")
    kw.pop("n_paths")
    if len(blocks) != len(days):
        raise SystemExit("REFUSED: P-13's blocks and its day set differ in length.")
    return Campaign("p13", list(blocks), [str(d) for d in days], kw)


def fv3c_campaign(rd: Path) -> Campaign:
    """FV3-C's development campaign: `ftp_sweep.fv3c_campaign` (D-505's, = `zero_edge_decomposition.run_fv3c`'s engine
    call argument for argument), its session dates from the same rebuild (`zero_edge_decomposition.fv3_trades`)."""
    import ftp_sweep as fs
    import zero_edge_decomposition as zd

    blocks, kw, seed = fs.fv3c_campaign(rd, n_paths=1, horizon=zd.HORIZON)
    kw = dict(kw)
    kw.pop("n_paths")
    _, days, _ = zd.fv3_trades(rd)
    if len(blocks) != len(days):
        raise SystemExit("REFUSED: FV3-C's blocks and its day set differ in length.")
    return Campaign("fv3c", list(blocks), [str(d) for d in days], kw)


def plans(rd: Path, need_noclose: bool, v12_of: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """{campaign: {table: policy}} -- each campaign's own v12 policy, and D-502's no-closure table (read through its
    result's manifest, `a3_compliance.noclose_policy`)."""
    out = {name: {"v12": pol} for name, pol in v12_of.items()}
    if need_noclose:
        import a3_compliance as a3

        nc = a3.noclose_policy(rd)
        for name in out:
            out[name]["noclose"] = nc
    return out


# ------------------------------------------------------------------------------------------------ the engine call


def arm_blocks(c: Campaign, arm: str) -> list:
    """The arm's blocks exactly as `gate.run_gate` builds them: as traded (`point`), or every R shifted to its own bound
    (`verdict`, the gate row's lower-bound arm)."""
    from propedge.campaign.gate import shifted_blocks

    if arm == "point":
        return list(c.blocks)
    if arm != "verdict":
        raise ValueError(f"arm must be 'point' or 'verdict', got {arm!r}")
    kw = c.kw
    delta = None
    if kw.get("e_by_rr") is not None:
        delta = {float(k): float(kw["lb_by_rr"][k]) - float(kw["e_by_rr"][k]) for k in kw["e_by_rr"]}
    return shifted_blocks(c.blocks, float(kw["lb"]) - float(kw["e"]), delta)


def engine_args(kw: dict, arm: str, blocks: list, *, risk_policy: Any = None,
                purchase_budget: tuple[int, int] | None = None, wallet_stop: float | None = None,
                pause_after_funded: int | None = None, seat_ramp: int | None = None) -> dict[str, Any]:
    """What `gate.run_gate` hands `SharedDayDraws` and `simulate_lockstep_campaign` hands `simulate_lockstep_path` for
    one path of this campaign at this arm (0 % denial), as a dict: `draws` (the shared draws' arguments, all but the
    blocks, seed and replay), `path` (the path's arguments, all but the horizon, seed and draw factories). The funded
    horizon is the replay's ("never", the Studio's), the only argument a replay changes besides the order of days.

    D-630's entry options (`wallet_stop`, `pause_after_funded`, `seat_ramp`) reach the path when the caller gives them
    or when the campaign's gate arguments (`kw`) carry them -- where `gate.run_gate` reads them, as `routing_rule` is
    read here -- the caller's first; absent from both, the arguments are exactly as before."""
    from propedge.campaign.lockstep import ConductModel, check_purchase_budget
    from propedge.campaign.payout_method import payout_method_terms
    from propedge.contract.payout_timing import DEFAULT_PAYOUT_TIMING, check_payout_timing
    from propedge.contract.rules import load_rules
    from propedge.outcomes.settlement import default_trade_log_settlement

    flip = kw.get("flip")
    if flip is not None and arm == "verdict":
        flip = flip.at_lower_bound()
    rules = kw["rules"]
    terms = payout_method_terms("aeropay", ledger=load_rules())          # run_gate's payout_method, its lag from the ledger
    draws = dict(protocol=kw["protocol"], mode=kw.get("mode", "rotation"), sizing=kw["sizing"],
                 settlement=kw.get("settlement") or default_trade_log_settlement(list(blocks)),
                 markets=kw.get("markets"), route_able=(kw.get("routing", "longest_waiting") == "able"),
                 cross_account=bool(kw.get("cross_account", False)), flip=flip,
                 hold_to_own_exit=bool(kw.get("hold_to_own_exit", False)), one_at_a_time=kw.get("one_at_a_time"))
    if kw.get("routing_rule") is not None:     # D-568: only when set, so every recorded replay is unchanged
        draws["routing_rule"] = kw["routing_rule"]
    path = dict(edge=0.0, rules=rules, initial_bankroll=float(kw["bankroll"]),
                max_concurrent_accounts=int(kw["accounts"]), subscription=float(rules.subscription),
                billing_days=int(rules.billing_days), activation=float(rules.activation),
                payout_lag_days=int(terms.lag_days), max_concurrent_combines=int(kw.get("combines", 1)),
                max_total_accounts=kw.get("total_accounts"),
                conduct=ConductModel(rtp=bool(kw.get("rtp", True)), enforcement_p=0.0),
                risk_policy=kw.get("risk_policy") if risk_policy is None else risk_policy,
                payout_timing=check_payout_timing(kw.get("payout_timing") or DEFAULT_PAYOUT_TIMING),
                combine_max_days=COMBINE_MAX_DAYS, funded_horizon_days=FUNDED_HORIZON)
    if purchase_budget is not None:
        path["purchase_budget"] = check_purchase_budget(purchase_budget)
    wallet_stop = kw.get("wallet_stop") if wallet_stop is None else wallet_stop
    pause_after_funded = kw.get("pause_after_funded") if pause_after_funded is None else pause_after_funded
    seat_ramp = kw.get("seat_ramp") if seat_ramp is None else seat_ramp
    if wallet_stop is not None or pause_after_funded is not None or seat_ramp is not None:
        # D-630: the engine's three entry options, each in the path's arguments only when given
        from propedge.campaign.lockstep import check_pause_after_funded, check_seat_ramp, check_wallet_stop

        if wallet_stop is not None:
            path["wallet_stop"] = check_wallet_stop(wallet_stop)
        if pause_after_funded is not None:
            path["pause_after_funded"] = check_pause_after_funded(pause_after_funded)
        if seat_ramp is not None:
            path["seat_ramp"] = check_seat_ramp(seat_ramp, path["max_total_accounts"])
    return {"draws": draws, "path": path, "seed": int(kw["seed"])}


def replay(blocks: list, args: dict[str, Any], horizon: int | None = None):
    """The as-happened replay of `blocks` from a fresh start: campaign day 0 the purchase evening, day k the k-th
    block's session; `horizon` sessions (all of them when None)."""
    from propedge.campaign.lockstep import simulate_lockstep_path
    from propedge.campaign.shared_days import SharedDayDraws

    n = len(blocks) if horizon is None else int(horizon)
    sd = SharedDayDraws({0: list(blocks[:n])}, seed=args["seed"], replay=True, **args["draws"])
    return simulate_lockstep_path(args["draws"]["protocol"], seed=args["seed"], horizon_days=n + 1,
                                  **args["path"], **sd.lockstep_kwargs())


# ------------------------------------------------------------------------------------------------ one slice


def _longest_gap(events: list[int], horizon: int) -> int:
    """The longest stretch of sessions without an event: from day 0 to the first, between events, from the last to the
    horizon's end (the whole horizon when there is none)."""
    marks = [0] + sorted(int(d) for d in events) + [int(horizon)]
    return int(max(b - a for a, b in zip(marks, marks[1:])))


def slice_measures(lp, horizon: int, subscription: float) -> dict[str, Any]:
    """One slice's readings from its `LockstepPath` (cash at each close, day 0 the purchase evening)."""
    p = lp.path
    init = float(p.initial_bankroll)
    cash = np.asarray(p.cash_series, dtype=float)
    pass_days = sorted(int(c.resolved_on) for c in lp.combines if c.passed and c.resolved_on is not None)
    pay_days: list[int] = []
    if p.days_to_first_payout is not None:
        pay_days = [int(p.days_to_first_payout)]
        for g in p.payout_gaps:
            pay_days.append(pay_days[-1] + int(g))
    net = float(cash[-1] - init)
    rel = np.concatenate([[0.0], cash - init])
    dd_start = float(max(0.0, -rel.min()))
    dd_high = float((np.maximum.accumulate(rel) - rel).max())
    return {"end_net": net, "positive": bool(net > 0), "passes": len(pass_days), "payouts": len(pay_days),
            "payout_dollars": float(p.total_payouts), "no_pass": not pass_days, "no_payout": not pay_days,
            "days_to_first_pass": float(pass_days[0]) if pass_days else float("nan"),
            "days_to_first_payout": float(pay_days[0]) if pay_days else float("nan"),
            "longest_pass_gap": _longest_gap(pass_days, horizon), "longest_payout_gap": _longest_gap(pay_days, horizon),
            "drawdown_from_start": dd_start, "drawdown_from_high": dd_high,
            "needed_bankroll": dd_start + float(subscription)}


def run_chunk(task: tuple) -> list[dict[str, Any]]:
    """A worker's share: (config, arm, blocks, dates, args, [(start, horizon), ...]) -> the slices' rows."""
    config, arm, blocks, dates, args, items = task
    sub = float(args["path"]["subscription"])
    out = []
    for start, h in items:
        lp = replay(blocks[start:start + h], args)
        if len(lp.path.cash_series) != h + 1:
            raise RuntimeError(f"{config} {arm} start {start} horizon {h}: {len(lp.path.cash_series)} closes, "
                               f"not {h + 1}")
        out.append({"section": "slice", "config": config, "arm": arm, "horizon": int(h), "start_day": int(start),
                    "start_date": dates[start], **slice_measures(lp, h, sub)})
    return out


def slice_items(n_days: int, horizons=HORIZONS) -> list[tuple[int, int]]:
    """Every (start, horizon) with the horizon inside the window."""
    return [(s, int(h)) for h in horizons for s in range(n_days) if s + int(h) <= n_days]


# ------------------------------------------------------------------------------------------------ the summary


def summarise(slices: pd.DataFrame) -> pd.DataFrame:
    """One row per (config, arm, horizon) in the order first seen."""
    rows = []
    for (config, arm, h), g in slices.groupby(["config", "arm", "horizon"], sort=False):
        net = g["end_net"].astype(float).to_numpy()

        def q(col: str, p: float) -> float:
            return float(np.percentile(g[col].astype(float).to_numpy(), p))

        rows.append({"section": "summary", "config": config, "arm": arm, "horizon": int(h), "n_slices": int(len(g)),
                     "share_positive": float(g["positive"].astype(bool).mean()),
                     "net_p5": float(np.percentile(net, 5)), "net_p10": float(np.percentile(net, 10)),
                     "net_median": float(np.median(net)), "net_p90": float(np.percentile(net, 90)),
                     "net_worst": float(net.min()),
                     "passes_p10": q("passes", 10), "passes_median": q("passes", 50),
                     "payouts_p10": q("payouts", 10), "payouts_median": q("payouts", 50),
                     "share_no_pass": float(g["no_pass"].astype(bool).mean()),
                     "share_no_payout": float(g["no_payout"].astype(bool).mean()),
                     "longest_pass_gap_p90": q("longest_pass_gap", 90),
                     "longest_payout_gap_p90": q("longest_payout_gap", 90),
                     "needed_bankroll_p95": q("needed_bankroll", 95)})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------ the identity


def studio_run(store: Path, arm: str) -> Path:
    runs = sorted((Path(store) / "runs").glob(STUDIO_RUNS[arm]))
    if not runs:
        raise SystemExit(f"REFUSED: no Studio run {STUDIO_RUNS[arm]} under {Path(store) / 'runs'}.")
    return runs[-1]


def studio_problems(lp, run_dir: Path) -> list[str]:
    """Our full-window replay against a Studio replay: cash by day re-based to the Studio's bankroll, to the cent (its
    file is rounded to the cent), and the path's totals exactly."""
    pay = json.loads((Path(run_dir) / "payload.json").read_text(encoding="utf-8"))
    sp = pay["replay"]["path"]
    cash = pd.read_csv(Path(run_dir) / "replay_cash.csv")
    ours = np.asarray(lp.path.cash_series, dtype=float) - float(lp.path.initial_bankroll) + float(sp["initial_bankroll"])
    theirs = cash["campaign_cash"].to_numpy(float)
    out = []
    if len(ours) != len(theirs):
        return [f"{len(ours)} closes against the Studio's {len(theirs)}"]
    diff = np.abs(np.round(ours, 2) - theirs)
    if (diff > 0.0051).any():
        i = int(np.argmax(diff > 0.0051))
        out.append(f"cash on day {i} ({cash['date'].iloc[i]}): {ours[i]:.2f} against the Studio's {theirs[i]:.2f} "
                   f"({int((diff > 0.0051).sum())} days differ)")
    for k in STUDIO_PATH_KEYS:
        mine, want = getattr(lp.path, k), sp.get(k)
        if not ((mine is None and want is None) or (mine is not None and want is not None
                                                      and abs(float(mine) - float(want)) <= TOTAL_TOL)):
            out.append(f"{k}: {mine!r} against the Studio's {want!r}")
    return out


def identity(c: Campaign, store: Path) -> list[dict[str, Any]]:
    """P-13's full-window replay at both arms against the Studio's mirror replays; refused on any difference."""
    rows = []
    for arm in ("verdict", "point"):
        run = studio_run(store, arm)
        t0 = time.time()
        lp = replay(arm_blocks(c, arm), engine_args(c.kw, arm, c.blocks))
        bad = studio_problems(lp, run)
        if bad:
            raise SystemExit(f"REFUSED (D-508): P-13's {arm} replay is not the Studio's ({run.name}) -- "
                             + "; ".join(bad[:6]))
        print(f"identity HOLDS: P-13 {arm} full-window replay = the Studio's {run.name} ({len(c.blocks)} sessions, "
              f"cash to the cent, totals equal; {time.time() - t0:.1f} s)", flush=True)
        rows.append({"section": "identity", "config": "p13", "arm": arm, "holds": True, "studio_run": run.name,
                     "check": "the full-window replay equals the Studio's mirror replay: campaign cash by day re-based to "
                              "its bankroll to the cent; " + ", ".join(STUDIO_PATH_KEYS) + " equal (dollars to 1e-6)",
                     "final_net": float(lp.path.final_cash - lp.path.initial_bankroll),
                     "total_payouts": float(lp.path.total_payouts), "total_fees": float(lp.path.total_fees)})
    return rows


# ------------------------------------------------------------------------------------------------ the study


def run_slices(jobs: list[tuple], workers: int, chunk: int = 60) -> list[dict[str, Any]]:
    """Every job's slices, across a guarded pool of processes (or here); rows in job then item order."""
    from propedge.campaign.lockstep import _WorkerEnvironment, path_pool

    tasks = []
    for config, arm, blocks, dates, args, items in jobs:
        for j in range(0, len(items), chunk):
            tasks.append((config, arm, blocks, dates, args, items[j:j + chunk]))
    pool, n = path_pool(int(workers), n_tasks=len(tasks), memory_per_worker_gb=WORKER_MEMORY_GB) \
        if int(workers) > 1 else (None, 1)
    print(f"{sum(len(t[5]) for t in tasks)} slices in {len(tasks)} tasks on {n} process(es)", flush=True)
    t0 = time.time()
    out: list[dict[str, Any]] = []
    if pool is None:
        for i, t in enumerate(tasks):
            out.extend(run_chunk(t))
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f} s", flush=True)
        return out
    try:
        with _WorkerEnvironment():
            futures = [pool.submit(run_chunk, t) for t in tasks]
        for i, f in enumerate(futures):
            out.extend(f.result())
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f} s", flush=True)
    finally:
        pool.shutdown()
    return out


def study(rd: Path, results_dir: Path | None, *, campaigns: dict[str, Campaign] | None = None,
          configs=CONFIGS, horizons=HORIZONS, workers: int = 1, store: Path = STUDIO_STORE, check_only: bool = False,
          record: bool = True, plans_override: dict | None = None, check_studio: bool = True) -> int:
    """The identity first, then every configuration's slices; the file. `campaigns`, `plans_override` and
    `check_studio` are test seams (toy campaigns, a stand-in for the no-closure table, no Studio on disk)."""
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    t_all = time.time()
    need = {c[2] for c in configs}
    if campaigns is None:
        campaigns = {}
        if "p13" in need or check_studio:
            print("P-13's campaign from the A3 rung cache...", flush=True)
            campaigns["p13"] = p13_campaign()
        if "fv3c" in need and not check_only:
            print("FV3-C's development campaign...", flush=True)
            campaigns["fv3c"] = fv3c_campaign(rd)
    idents = identity(campaigns["p13"], store) if check_studio else []
    if check_only:
        print(f"the identity holds; nothing written (--check). {time.time() - t_all:.0f} s")
        return 0
    pl = plans_override or plans(rd, any(c[3] == "noclose" for c in configs),
                                 {k: v.kw["risk_policy"] for k, v in campaigns.items()})
    jobs = []
    for config, arm, camp, table, budget in configs:
        c = campaigns[camp]
        blk = arm_blocks(c, arm)
        args = engine_args(c.kw, arm, c.blocks, risk_policy=pl[camp][table], purchase_budget=budget)
        jobs.append((config, arm, blk, c.dates, args, slice_items(len(blk), horizons)))
    rows = run_slices(jobs, workers)
    sl = pd.DataFrame(rows, columns=list(SLICE_COLS))
    summ = summarise(sl)
    res = pd.concat([sl, summ], ignore_index=True)[list(SLICE_COLS) + list(SUMMARY_COLS)]
    seconds = time.time() - t_all
    if record:
        counter = VariantCounter(path=rd / "variants.jsonl")
        for config, arm, camp, table, budget in configs:
            counter.record(prereg_id=FAMILY_ID, seed=int(campaigns[camp].kw["seed"]), exploratory=True,
                           params={"study": "customer slices (D-508)", "config": config, "arm": arm,
                                   "campaign": camp, "table": table, "budget": list(budget) if budget else None,
                                   "horizons": list(horizons)},
                           label=f"D-508's customer slices: {config} ({arm})")
    params = {"decision": DECISION, "configs": [{"config": c, "arm": a, "campaign": k, "table": t,
                                                 "budget": list(b) if b else None} for c, a, k, t, b in configs],
              "horizons": list(horizons), "funded_horizon_days": FUNDED_HORIZON,
              "campaigns": {k: {"sessions": len(v.blocks), "first": v.dates[0], "last": v.dates[-1],
                                "seed": int(v.kw["seed"]), "one_at_a_time": v.kw.get("one_at_a_time"),
                                "policy_v12": getattr(v.kw["risk_policy"], "id", None),
                                "capacity": int(v.kw["protocol"].trades_per_day)} for k, v in campaigns.items()},
              "order": "historical (the engine's as-happened replay, D-130; no resampling)",
              "bankroll": "unbound (the gate's UNBOUND_BANKROLL); needed_bankroll = drawdown from start + one subscription",
              "percentiles": "numpy linear", "placement": "off", "enforcement_p": 0.0,
              "studio_identity": idents, "workers": int(workers),
              "seconds": round(seconds, 1)}
    write_result(res, RESULT, script=SCRIPT, seed=int(next(iter(campaigns.values())).kw["seed"]), exploratory=True,
                 results_dir=results_dir, variant_count=len(configs), parameters=params,
                 notes={"status": READING + "; no selection, no money decision",
                        "variant_count_rule": f"one reading per configuration and arm, under {FAMILY_ID}",
                        "seeds": "a replay draws nothing; each campaign's own seed is passed as its run passed it"},
                 description="EXPLORATORY (D-508): every trading day of each configuration's development window as a "
                             "fresh start, the campaign replayed forward on its trades in historical order for 21, 63 "
                             "and 126 trading days; per slice the net, passes, payouts, drawdowns, first events and "
                             "longest gaps (section slice), their distributions per configuration, arm and horizon "
                             "(section summary); the Studio identity in the manifest; beside, never a gate.")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    show = summ.set_index(["config", "arm", "horizon"])[["n_slices", "share_positive", "net_p5", "net_p10",
                                                         "net_median", "net_worst", "share_no_payout",
                                                         "needed_bankroll_p95"]]
    print(show.round(3).to_string())
    print(f"written: {RESULT}.csv ({len(sl)} slices; {seconds:.0f} s)")
    return 0


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the Studio identity only; nothing written")
    ap.add_argument("--workers", type=int, default=1, help="slice workers (the memory guard may grant fewer)")
    ap.add_argument("--studio-store", default=str(STUDIO_STORE), help="the Campaign Studio's store")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    return study(rd, results_dir, workers=a.workers, store=Path(a.studio_store), check_only=a.check)


if __name__ == "__main__":
    raise SystemExit(main())
