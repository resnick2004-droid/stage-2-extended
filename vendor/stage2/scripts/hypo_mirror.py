"""HYPOTHETICAL (D-515): the pure-mirror hedge pair -- `hypothetical_hedge`, EXPLORATORY, NOT A CANDIDATE.

    python scripts/hypo_mirror.py --resolution-only      # the resolution reading and the choice; nothing written
    python scripts/hypo_mirror.py --workers 6            # the study; writes results/hypo_mirror.csv (+ _paths)

Cross-firm and cross-account hedging are prohibited (Topstep 13747047 / 10296582, Lucid 11404734; tier 1, D-145) and
that does not change. The operator (2026-11-01): "With no signal we can use a standard risk and RR and contract sizing
so that truncation is not an issue" and "make sure the brackets fully resolve" -- with two exactly mirrored accounts,
how certain, how fast and how costly is a pass, and then a payout? Every row, manifest and variant is labelled
`hypothetical_hedge`; nothing here is ranked, sized or carried into a protocol (D-515).

The mechanics, the declared resolution rule and the sizing arithmetic are `propedge.research.hypo_mirror`'s docstring
(written before the reading). In order:

1. **The resolution reading** -- every T24 slot's pair at 12.5 / 20 / 25 / 40-point stops at 1:1 on every development
   day (2020-01-02 .. 2026-07-16, A1's day set, the bars through the window guard): the unresolved share by the 15:10
   flatten overall and per year, the mirror's breaks (ties, touches, gaps), the minutes to resolution; then the
   declared rule picks the stop and the clock times (sections `resolution`, `choice`).
2. **The sizing** -- whole micros at the chosen stop: the Combine's two-win $1,600 (propsim D-08's 1:1 $1,500 plus the
   costs' margin) and the funded leg's 20 micros (the entry tier's allowance); the arithmetic (section `sizing`).
3. **The arms** -- two firms with Topstep's verified contract (Firm H's convention, D-203; `rules_for_method
   ('aeropay')`), five seats each, one pooled wallet (D-206), each firm a lockstep campaign with the fixed 1:1 legs
   (one trade an account a session), D-514's purchase budget of 20 in 21 trading days per firm (D-502) and the strict
   one-position-per-firm rule (D-429's five minutes): **b_mirror** (each clock trade one account long at one firm and
   one short at the other, the same bracket and size, `hypo_mirror.MirrorRouter`: Combine with Combine, funded with
   funded where possible), **a_unhedged** (the same clock trades, each to one account at one firm on a seeded coin's
   side; ten seats) and **one_firm** (one firm's five seats, the coin's side). Zero payout denial, no conduct model
   (placement off), 500 paths at seed 20261201, 504 sessions; the point arm and the bound-shifted arm (the coin side's
   trades at the one-sided 95 % bound of their mean R, the opposite side moved the same amount the other way -- the
   mirror's sum unchanged, `hypo_hedge.mirror_shift`).
4. **The readings** (section `arm`): pairs ending one pass / none / both, days to a pass, Combine fees per pass, the
   funded stage (days to a first payout, payouts per account and per pair, fees per payout, accounts breached), growth
   on the required bankroll and the required bankroll, payouts per month; the trades' settlement (section `trades`:
   the mirror's breaks among the clock trades, each side's mean R); and the customer slices (section `slices`: every
   start of the window in historical order at 21 / 63 / 126 sessions, `customer_slices.summarise`, the bound arm).

Writes `results/hypo_mirror.csv`, its per-path companion `results/hypo_mirror_paths.csv`, and the variants under
`D-515:hypothetical_hedge`.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
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

from propedge.research import hypo_hedge as hh  # noqa: E402
from propedge.research import hypo_mirror as hm  # noqa: E402

SCRIPT = "scripts/hypo_mirror.py"
DECISION = hm.DECISION
RESULT = "hypo_mirror"
SEED = 20261201
N_PATHS = 500
HORIZON = 504                              # FV3-C's gate horizon (config/fv3_corrected_portfolio.yaml)
HORIZONS = (21, 63, 126)
MARKET = "NQ"
FIRST, LAST = "2020-01-02", "2026-07-16"
BUDGET = (20, 21)                          # D-502 / D-514: 20 Combine purchases and resets in any 21 trading days
ACCOUNTS = 5                               # seats a firm (FV3-C's `accounts`, `combines`)
MARGIN = 49.0                              # FV3-C's `portfolio.margin`: one subscription
UNBOUND_BANKROLL = 100_000_000.0           # D-312: the bankroll an output
FUNDED_HORIZON_REPLAY = 100_000            # customer_slices' replay: a funded account lives to the slice's end
COMBINE_MAX_DAYS = 2000
LB_Z = 1.6448536269514722                  # one-sided 95 %
ARMS = (("one_firm", 1, hh.UNHEDGED), ("a_unhedged", 2, hh.UNHEDGED), ("b_mirror", 2, hh.HEDGED))
SHIFTS = ("point", "lower_bound")
CHUNK = 25
SLICE_CHUNK = 120
WORKER_GB = 0.6


# ------------------------------------------------------------------------------------------------ 1. resolution


def fee() -> float:
    from propedge.execution.fills import FillModel

    return float(FillModel.load("assumed").round_turn_by_instrument["MNQ"])


def day_set() -> list[str]:
    from propedge.research.atlas_walk import CACHE

    d = pd.read_parquet(CACHE / "A1" / "days.parquet")
    d = d[d["day_kind"].astype(str) != "x"]
    days = sorted(d["date"].astype(str))
    if days[0] != FIRST or days[-1] != LAST:
        raise SystemExit(f"REFUSED ({DECISION}): A1's day set runs {days[0]}..{days[-1]}, not {FIRST}..{LAST}.")
    return days


def walk_all(days: list[str], fee_rt: float) -> pd.DataFrame:
    """Every T24 slot's pair at every candidate stop on every day (the bars through the window guard)."""
    from propedge.data.bars import read_bars
    from propedge.research import atlas_local
    from propedge.research.atlas_walk import t24_slots

    bars = read_bars(MARKET, days[0], days[-1], "development", what="D-515 mirror resolution reading")
    by_day = {d: g for d, g in bars.groupby("day", sort=False)}
    slots = t24_slots()
    stops = [hm.ticks(s) for s in hm.STOPS_POINTS]
    out: list[dict] = []
    for d in days:
        o, h, l, c = (np.array([np.nan if x is None else x for x in v], dtype=float)
                      for v in atlas_local.day_arrays(by_day.get(d, bars.iloc[0:0])))
        out += hm.flatten_pairs(d, hm.day_pairs(o, h, l, c, slots, stops), fee_rt)
    return pd.DataFrame(out)


def ct(slot: int) -> str:
    m = (int(slot) + 17 * 60) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


# ------------------------------------------------------------------------------------------------ 2-3. the campaign


def trade_set(pairs: pd.DataFrame, choice: dict) -> pd.DataFrame:
    t = pairs[(pairs["stop_ticks"] == int(choice["stop_ticks"])) & (pairs["slot"].isin(choice["slots"]))]
    t = t.sort_values(["date", "entry", "slot"], kind="stable").reset_index(drop=True)
    t["coin"] = hm.coin_sides(len(t), SEED)
    return t


def cell_stats(t: pd.DataFrame) -> dict[str, float]:
    """The coin side's mean net R and its one-sided 95 % lower bound (iid normal; labelled), and each side's."""
    coin = np.where(t["coin"].to_numpy(int) > 0, t["long_r"].to_numpy(float), t["short_r"].to_numpy(float))
    n = len(coin)
    e = float(coin.mean())
    lb = float(e - LB_Z * coin.std(ddof=1) / np.sqrt(n))
    return {"trades": n, "e_coin": e, "lb_coin": lb, "delta_r": lb - e, "e_long": float(t["long_r"].mean()),
            "e_short": float(t["short_r"].mean()), "e_pair_sum": float((t["long_r"] + t["short_r"]).mean()),
            "share_coin_long": float((t["coin"] > 0).mean())}


def policy(sz: dict):
    from propedge.campaign.risk_policy import Leaf, Phase, RiskPolicy

    return RiskPolicy(id="d515_mirror_fixed_1to1", description="D-515's fixed whole-micro legs at 1:1, one trade an "
                      "account a session",
                      root=Phase(combine=Leaf(f"combine 1:1 {sz['combine_micros']} micros", float(sz["combine_risk"]),
                                              None, max_trades=1),
                                 funded=Leaf(f"funded 1:1 {sz['funded_micros']} micros", float(sz["funded_risk"]),
                                             None, max_trades=1)))


def setups(sz: dict, n_slots: int) -> tuple[hh.FirmSetup, hh.FirmSetup]:
    """(the resampled campaign's setup, the replay's): the fixed legs, rotation with the strict rule, `mae` settlement,
    Topstep's verified rules (aeropay), five seats, the budget, the placement off and 0 % denial."""
    from propedge.campaign.lockstep import ConductModel, check_purchase_budget
    from propedge.campaign.payout_method import payout_method_terms, rules_for_method
    from propedge.campaign.protocols import Protocol
    from propedge.contract.payout_timing import DEFAULT_PAYOUT_TIMING
    from propedge.contract.rules import load_rules

    proto = Protocol(name="d515_mirror", combine_rr=1.0, combine_risk=float(sz["combine_risk"]), funded_rr=1.0,
                     funded_risk=float(sz["funded_risk"]), trades_per_day=2 * int(n_slots),
                     max_concurrent_accounts=ACCOUNTS, family="hypothetical_hedge",
                     source="D-515: propsim D-08's 1:1 at $1,500 plus the costs' margin; the funded entry tier",
                     note=hm.LABEL)
    rules = rules_for_method("aeropay")
    terms = payout_method_terms("aeropay", ledger=load_rules())
    draws = dict(mode="rotation", sizing=None, settlement="mae", markets=None, route_able=False, cross_account=False,
                 flip=None, hold_to_own_exit=True, one_at_a_time=hm.GAP_MINUTES)
    path = dict(edge=0.0, rules=rules, initial_bankroll=UNBOUND_BANKROLL, max_concurrent_accounts=ACCOUNTS,
                subscription=float(rules.subscription), billing_days=int(rules.billing_days),
                activation=float(rules.activation), payout_lag_days=int(terms.lag_days),
                max_concurrent_combines=ACCOUNTS, max_total_accounts=ACCOUNTS,
                conduct=ConductModel(rtp=False, enforcement_p=0.0), risk_policy=policy(sz),
                payout_timing=DEFAULT_PAYOUT_TIMING, combine_max_days=COMBINE_MAX_DAYS, funded_horizon_days=HORIZON,
                purchase_budget=check_purchase_budget(BUDGET))
    camp = hh.FirmSetup(protocol=proto, draws=draws, path=path, bankroll=UNBOUND_BANKROLL)
    rep = hh.FirmSetup(protocol=proto, draws=draws, path={**path, "funded_horizon_days": FUNDED_HORIZON_REPLAY},
                       bankroll=UNBOUND_BANKROLL)
    return camp, rep


def arm_blocks(cell: list, opp: list, shift: str, delta: float) -> list:
    if shift == "point":
        return hh.doubled_blocks(cell, opp)
    c, o = hh.mirror_shift(cell, opp, delta, {1.0: delta})
    return hh.doubled_blocks(c, o)


# ------------------------------------------------------------------------------------------------ the jobs


def _paths_task(task: tuple) -> list[dict]:
    import warnings

    warnings.filterwarnings("ignore")
    arm, firms, mode, shift, blocks, setup, items, margin, horizon, fees = task
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=int(horizon)) for _, s in items]
    jps = hm.run_joint(specs, setup, n_firms=int(firms), mode=mode)
    out = []
    for (i, s), jp in zip(items, jps):
        r = hm.path_record(jp, margin=margin, subscription=fees[0], activation=fees[1])
        r.update({"arm": arm, "shift": shift, "path": int(i), "seed": int(s)})
        out.append(r)
    return out


def _slices_task(task: tuple) -> list[dict]:
    import warnings

    warnings.filterwarnings("ignore")
    arm, firms, mode, blocks, dates, setup, items, seed, sub = task
    specs = [hh.PathSpec(seed=int(seed), blocks=blocks[s:s + h], horizon_days=int(h) + 1, replay=True)
             for s, h in items]
    jps = hm.run_joint(specs, setup, n_firms=int(firms), mode=mode)
    out = []
    for (s, h), jp in zip(items, jps):
        n = len(jp.paths[-1].path.cash_series)
        if n != h + 1:
            raise RuntimeError(f"{arm} start {s} horizon {h}: {n} closes, not {h + 1}")
        out.append({"section": "slice", "config": arm, "arm": "verdict", "horizon": int(h), "start_day": int(s),
                    "start_date": dates[s], **hh.slice_measures(jp, int(h), sub)})
    return out


def _run(tasks: list[tuple], fn, workers: int) -> list[list[dict]]:
    from propedge.campaign.lockstep import _WorkerEnvironment, path_pool

    pool, n = (path_pool(int(workers), n_tasks=len(tasks), memory_per_worker_gb=WORKER_GB)
               if int(workers) > 1 else (None, 1))
    print(f"  {len(tasks)} tasks on {n} process(es)", flush=True)
    t0 = time.time()
    if pool is None:
        out = []
        for i, t in enumerate(tasks):
            out.append(fn(t))
            print(f"  {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f} s", flush=True)
        return out
    try:
        with _WorkerEnvironment():
            futures = [pool.submit(fn, t) for t in tasks]
        out = []
        for i, f in enumerate(futures):
            out.append(f.result())
            print(f"  {i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f} s", flush=True)
        return out
    finally:
        pool.shutdown()


# ------------------------------------------------------------------------------------------------ the study


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.campaign.lockstep import path_seeds

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--resolution-only", action="store_true", help="the reading and the choice only; nothing written")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--slice-starts", type=int, default=None, help="test seam: only the first starts")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    fee_rt = fee()
    days = day_set()

    # 1. the resolution reading, then the declared rule
    print(f"the resolution reading: {len(days)} days x 23 slots x {len(hm.STOPS_POINTS)} stops...", flush=True)
    pairs = walk_all(days, fee_rt)
    table = hm.resolution_table(pairs)
    years = sorted({int(d[:4]) for d in days})
    choice = hm.choose(table, years, fee_rt)
    pd.set_option("display.width", 250)
    show = table.assign(ct=table["slot"].map(ct))
    print(show.pivot(index="ct", columns="stop_points", values="unresolved_share").round(4).to_string())
    for p in choice["per_stop"]:
        print(f"  {p['stop_points']:g} pts: feasible={p['feasible']} qualifying={[ct(s) for s in p['qualifying_slots']]} "
              f"schedule={[ct(s) for s in p['schedule']]}")
    print(f"CHOSEN: {choice['stop_points']:g} points at {[ct(s) for s in choice['slots']]} "
          f"({time.time() - t_all:.0f} s)", flush=True)
    sz = hm.sizing(choice["stop_points"], fee_rt)
    print("sizing:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in sz.items()}, flush=True)
    if a.resolution_only:
        return 0

    # 2. the trades and the blocks
    t = trade_set(pairs, choice)
    st = cell_stats(t)
    cell, opp = hm.blocks(t, days)
    blocks = {s: arm_blocks(cell, opp, s, st["delta_r"]) for s in SHIFTS}
    camp, rep = setups(sz, len(choice["slots"]))
    fees = (float(camp.path["subscription"]), float(camp.path["activation"]))
    seeds = path_seeds(SEED, int(a.paths))
    print(f"  {st['trades']} clock trades on {len(days)} sessions; coin side e {st['e_coin']:+.4f} R, bound "
          f"{st['lb_coin']:+.4f} R", flush=True)

    # 3. the arms
    tasks = []
    for arm, firms, mode in ARMS:
        for s in SHIFTS:
            for j in range(0, len(seeds), CHUNK):
                tasks.append((arm, firms, mode, s, blocks[s], camp, list(enumerate(seeds))[j:j + CHUNK], MARGIN,
                              HORIZON, fees))
    print(f"the arms: {len(ARMS)} x {len(SHIFTS)} x {len(seeds)} paths...", flush=True)
    paths = [r for chunk in _run(tasks, _paths_task, a.workers) for r in chunk]

    # 4. the slices (the bound-shifted arm, as D-508's verdict rows)
    vb = blocks["lower_bound"]
    n_days = len(vb)
    starts = n_days if a.slice_starts is None else int(a.slice_starts)
    items = [(s, h) for h in HORIZONS for s in range(min(starts, n_days)) if s + h <= n_days]
    sub = float(rep.path["subscription"])
    s_tasks = [(arm, firms, mode, vb, days, rep, items[j:j + SLICE_CHUNK], SEED, sub)
               for arm, firms, mode in ARMS for j in range(0, len(items), SLICE_CHUNK)]
    print(f"the slices: {len(ARMS)} arms x {len(items)} slices...", flush=True)
    sl = pd.DataFrame([r for chunk in _run(s_tasks, _slices_task, a.workers) for r in chunk])
    import customer_slices as cs

    summ = cs.summarise(sl)
    return write(rd, results_dir, table, choice, sz, t, st, paths, summ, len(seeds), time.time() - t_all,
                 starts=starts, n_days=n_days)


def write(rd: Path, results_dir: Path | None, table: pd.DataFrame, choice: dict, sz: dict, t: pd.DataFrame, st: dict,
          paths: list[dict], summ: pd.DataFrame, n_paths: int, seconds: float, *, starts: int, n_days: int) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    arm_desc = {"one_firm": "reference: one firm's five seats, each clock trade to one account on the coin's side",
                "a_unhedged": "two firms, ten seats, each clock trade to one account on the coin's side (unhedged)",
                "b_mirror": "two firms, each clock trade one account long at one firm and one short at the other, the "
                            "same 1:1 bracket and whole-micro size (Combine with Combine, funded with funded where "
                            "possible)"}
    rows: list[dict] = []
    res = table.copy()
    res.insert(0, "section", "resolution")
    res["ct"] = res["slot"].map(ct)
    res["qualifies"] = [hm.qualifies(r, sorted({int(c[-4:]) for c in table.columns if c.startswith("unresolved_2")}))
                        for _, r in table.iterrows()]
    for p in choice["per_stop"]:
        rows.append({"section": "choice", "stop_points": p["stop_points"], "stop_ticks": p["stop_ticks"],
                     "feasible": p["feasible"], "qualifying_slots": " ".join(ct(s) for s in p["qualifying_slots"]),
                     "schedule": " ".join(ct(s) for s in p["schedule"]), "n_schedule": len(p["schedule"]),
                     "chosen": bool(p["stop_ticks"] == choice["stop_ticks"])})
    rows.append({"section": "sizing", **sz})
    tr = {"section": "trades", "stop_points": choice["stop_points"], "slots": " ".join(ct(s) for s in choice["slots"]),
          **st}
    for k in hm.PAIR_CLASSES:
        tr[f"share_{k}"] = float((t["class"] == k).mean())
    tr["share_unresolved_any"] = float(t["unresolved"].mean())
    tr["share_gap_any"] = float(((t["long_gap_ticks"] > 0) | (t["short_gap_ticks"] > 0)).mean())
    tr["minutes_to_resolve_p50"] = float(t["minutes_to_resolve"].median())
    tr["minutes_to_resolve_p99"] = float(np.percentile(t["minutes_to_resolve"], 99))
    by_slot = t.groupby("slot")["class"].apply(lambda s: float((s == "mirror").mean()))
    for s, v in by_slot.items():
        tr[f"share_mirror_{ct(s).replace(':', '')}"] = v
    rows.append(tr)
    for arm, firms, mode in ARMS:
        for s in SHIFTS:
            recs = [r for r in paths if r["arm"] == arm and r["shift"] == s]
            rows.append({"section": "arm", "arm": arm, "firms": firms, "mode": mode, "shift": s,
                         "arm_text": arm_desc[arm], **hm.readings(recs, margin=MARGIN)})
    summ = summ.copy()
    summ["section"] = "slices"
    summ["arm"] = summ["config"]
    summ = summ.drop(columns=["config"])
    summ["shift"] = "lower_bound"
    out = pd.concat([res, pd.DataFrame(rows), summ], ignore_index=True)
    out.insert(0, "label", hm.TAG)
    hm.require_label(out.to_dict("records"))
    per_path = pd.DataFrame([{"label": hm.TAG, "arm": r["arm"], "shift": r["shift"], "path": r["path"],
                              "seed": r["seed"], "net": r["net"], "fees": r["fees"],
                              "combine_fees": r["combine_fees"], "activation_fees": r["activation_fees"],
                              "payouts_dollars": r["payouts_dollars"], "needed": r["needed"],
                              "combines_started": r["combines_started"], "combines_resolved": len(r["resolved"]),
                              "passes": len(r["pass_days"]), "payouts": len(r["pay_days"]),
                              "funded_accounts": r["funded_accounts"], "funded_breached": r["funded_breached"],
                              "pairs": r["pairs"], "funded_pairs": r["funded_pairs"],
                              **{f"combine_pairs_{k}": v for k, v in r["combine_pair_outcomes"].items()},
                              "pass_days": " ".join(str(d) for d in r["pass_days"]),
                              "pay_days": " ".join(str(d) for d in r["pay_days"]),
                              **{f"deal_{k}": (v if not isinstance(v, list) else " ".join(str(x) for x in v))
                                 for k, v in r["deal"].items()}} for r in paths])
    hm.require_label(per_path.to_dict("records"))
    counter = VariantCounter(path=Path(rd) / "variants.jsonl")
    for arm, firms, mode in ARMS:
        counter.record(prereg_id=hm.VARIANT, seed=SEED, exploratory=True,
                       params={"study": "the pure-mirror hedge pair", "decision": DECISION, "arm": arm, "mode": mode,
                               "firms": firms, "paths": n_paths, "stop_points": choice["stop_points"],
                               "slots": [ct(s) for s in choice["slots"]]},
                       label=f"{hm.TAG}: {arm} ({DECISION}) -- {hm.LABEL}")
    params = {"decision": DECISION, "label": hm.TAG, "status": hm.LABEL, "seed": SEED, "n_paths": n_paths,
              "horizon": HORIZON, "horizons": list(HORIZONS), "slice_starts": starts, "sessions": n_days,
              "window": [FIRST, LAST], "stops_points": list(hm.STOPS_POINTS), "delay": hm.DELAY,
              "rule": {"unresolved_overall_max": hm.UNRESOLVED_OVERALL, "unresolved_year_max": hm.UNRESOLVED_YEAR,
                       "spacing_quantile": hm.SPACING_Q, "gap_minutes": hm.GAP_MINUTES, "max_slots": hm.MAX_SLOTS,
                       "text": "propedge/research/hypo_mirror.py docstring section 2, declared before the reading"},
              "choice": {"stop_points": choice["stop_points"], "slots": [ct(s) for s in choice["slots"]]},
              "sizing": {k: v for k, v in sz.items()},
              "arms": [{"arm": a_, "firms": f, "mode": m, "text": arm_desc[a_]} for a_, f, m in ARMS],
              "firms": "two firms with Topstep's verified contract (Firm H's convention, D-203; rules_for_method"
                       "('aeropay')), five seats each, one pooled wallet (D-206)",
              "protocol": "fixed whole-micro 1:1 legs (RiskPolicy d515_mirror_fixed_1to1, one trade an account a "
                          "session), rotation, the strict rule per firm (5 min), mae settlement, no sizing rule (no "
                          f"tier, no room cap), purchase budget {list(BUDGET)} per firm, {ACCOUNTS} seats per firm",
              "bound": {"delta_r": st["delta_r"], "rule": "the coin side's mean net R at its one-sided 95 % iid normal "
                        "lower bound; the opposite side moved the same amount the other way (hypo_hedge.mirror_shift)"},
              "coin": f"numpy default_rng({SEED}), one fair draw per clock trade in historical order",
              "conduct": "ConductModel(rtp=False, enforcement_p=0.0): placement off, 0 % denial",
              "bankroll": f"unbound; required bankroll = deepest pooled loss from the start + {MARGIN:g} "
                          "(portfolio.measures), growth on it at p90",
              "costs": f"a tick at entry, MNQ round turn {sz['fee_round_turn']} (config/fills.yaml, 8284213), the "
                       "exit's ticks (stop 1, target 0, flatten 2); $0.50 a tick a micro",
              "slices": "customer_slices' replay and summary (D-508), the bound-shifted arm, pooled cash",
              "seconds": round(float(seconds), 1), "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"}
    write_result(out, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir, parameters=params,
                 notes={"decisions": ["D-145", "D-153", "D-203", "D-206", "D-514", "D-515"], "status": hm.LABEL,
                        "label": hm.TAG},
                 description="HYPOTHETICAL (hypothetical_hedge, D-515): the pure-mirror hedge pair -- no signal, fixed "
                             "clock entries, one account long and one short at the same bar with the same 1:1 bracket "
                             "and whole-micro size at two Topstep-rule firms on one pooled wallet, beside the unhedged "
                             "clock trades; the resolution reading and choice, the sizing, pass and payout certainty, "
                             "speed and cost, and the customer slices. Prohibited conduct (tier 1); never a candidate.")
    write_result(per_path, f"{RESULT}_paths", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 parameters={"result": f"{RESULT}.csv", "label": hm.TAG},
                 notes={"status": hm.LABEL, "companion_of": f"{RESULT}.csv", "label": hm.TAG},
                 description=f"HYPOTHETICAL (hypothetical_hedge): the per-path record of {RESULT}.csv.")
    show = ["arm", "shift", "growth_on_required", "required_p90", "passes_mean", "pass_rate_per_combine",
            "share_combine_pairs_one_pass", "share_combine_pairs_no_pass", "share_combine_pairs_both_pass",
            "days_to_first_pass_p50", "combine_fees_per_pass", "days_activation_to_first_payout_p50",
            "payouts_per_funded_account", "share_funded_breached", "all_fees_per_payout", "payouts_per_month_mean"]
    print(hm.LABEL)
    print(pd.DataFrame([r for r in rows if r["section"] == "arm"])[show].round(4).to_string(index=False))
    print(summ[["arm", "horizon", "share_positive", "net_p10", "share_no_payout", "needed_bankroll_p95"]]
          .round(3).to_string(index=False))
    print(f"written: {RESULT}.csv and {RESULT}_paths.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
