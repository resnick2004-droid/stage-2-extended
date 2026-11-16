"""HYPOTHETICAL (D-619): the hedge cycle on P-16's executions -- `hypothetical_hedge`, EXPLORATORY, NOT A CANDIDATE.

    python scripts/hedge_cycle.py --check            # the identity at 2 paths, tiny libraries and cycles; nothing written
    python scripts/hedge_cycle.py --workers 3        # the study (from a clean checkout, D-474): results/hedge_cycle.csv

Cross-firm and cross-account hedging are prohibited (Topstep 13747047 / 10296582, Lucid 11404734; tier 1, D-145) and
that does not change. The design, its defaults, the measures and the ranking are D-619's (declared before anything was
read); the cycle and its pieces are `propedge.research.hedge_cycle`'s. In order:

1. **The inputs** -- P-16's cell (`rc150_dev_test.build_cells`, its content hash checked), its blocks, each R's e and
   0.05 bound (`atlas_a3.bounds`), P-16's engine call (`atlas_a3.gate_kwargs` -> `customer_slices.engine_args` ->
   `hypo_hedge.setup_from_engine_args`); the three firms' setups -- Topstep's (P-16's own), Lucid's
   (`rc150_firm_split.lucid_setup`, D-575) and the static firm's (`static_setup`); the hedge table (P-16's walk at a
   200-tick stop, every mark walked long and short, each day's first offered mark at R = 1, 20 micros) and the
   survivor table (each day's first offered P-16 trade at R = 1, per micro).
2. **The identity, refusing** -- the episode runner on P-16's setup unchanged (five seats, the 20-in-21 budget) at
   P-16's campaign seed over 504 sessions reproduces `results/rc_s150_all_gate_paths.csv`'s `gate` paths at both
   shifts (final cash, fees, payouts) for the first `IDENTITY_PATHS` paths.
3. **The libraries** -- for each firm, seat count and arm, `N_EPISODES` evaluation episodes from fresh (the engine's
   single-firm path over `EPISODE_HORIZON` sessions, cut at its first pass).
4. **The cycles** -- for each second firm and seat count, 500 paths of 504 sessions at both arms
   (`hedge_cycle.simulate_path`), the readings (`hedge_cycle.readings`) and, on the bound arm, D-619 (7)'s ranking.

Writes `results/hedge_cycle.csv` (sections identity, tables, episodes, cell, ranking) and `results/hedge_cycle_paths.csv`,
EXPLORATORY, every row labelled `hypothetical_hedge`, variants under `D-619:hypothetical_hedge`.
"""
from __future__ import annotations

import argparse
import dataclasses
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

from propedge.research import hedge_cycle as hc  # noqa: E402
from propedge.research import hypo_hedge as hh  # noqa: E402

SCRIPT = "scripts/hedge_cycle.py"
DECISION = hc.DECISION
RESULT = "hedge_cycle"
SEED = 20261214                            # D-619 (5): fresh, used nowhere else
N_PATHS = 500
HORIZON = 504
EPISODE_HORIZON = 252
N_EPISODES = 1000
SEATS = (1, 2, 3, 4, 5)
SECOND = ("lucid", "static", "topstep")
KINDS = ("topstep", "lucid", "static")     # the libraries' firms (Topstep is always firm A)
SHIFTS = ("point", "lower_bound")
BUDGET = (20, 21)                          # D-619 (1): 20 in 21 trading days per firm, as directed
IDENTITY_PATHS = 4
TOLERANCE = 0.10                           # D-619 (7)
MARGIN = 49.0                              # one Topstep subscription (FV3-C's portfolio.margin)
EPISODE_CHUNK = 100
CYCLE_CHUNK = 50


# ------------------------------------------------------------------------------------------------ 1. the inputs


def static_setup(base: hh.FirmSetup) -> hh.FirmSetup:
    """D-619 (2b): P-16's (Topstep's) setup with the static floor, the close-only settlement and the green-day pass."""
    draws = dict(base.draws)
    if "settlement" not in draws:
        raise SystemExit("REFUSED (D-619): P-16's draws carry no settlement to replace with the close-only one.")
    draws["settlement"] = "legacy"         # the trade's own outcome: no intraday breach (the close is checked)
    path = dict(base.path)
    path.update(rules=hc.static_rules(path["rules"]), combine_account_cls=hc.StaticCombineAccount)
    return dataclasses.replace(base, draws=draws, path=path)


def _forced_walk(I: dict, side: int) -> pd.DataFrame:
    """P-16's walk at the hedge's 200-tick stop with every mark's coin forced to `side`: the cell's trades (D-533's cut)."""
    import rc_width_screen as W

    from propedge.research import resolved_coin as rc

    orig = rc.coin_table

    def forced(*a, **k):
        return {key: int(side) for key in orig(*a, **k)}

    rc.coin_table = forced
    try:
        b = W.build(I, (hc.HEDGE_STOP_TICKS,))
    finally:
        rc.coin_table = orig
    t = b["cells"][rc.reentry_cell_name(hc.HEDGE_STOP_TICKS, "all")]["trades"]
    if t is None or not len(t):
        raise SystemExit("REFUSED (D-619): the 200-tick walk offers no trade.")
    return t


def _first_marks(t: pd.DataFrame) -> pd.DataFrame:
    return t.sort_values(["date", "decision_slot_minutes"], kind="stable").groupby("date", sort=False).head(1) \
            .set_index("date")


#: the hedge's last bar: P-16's flatten at 15:08 CT on the trading-day clock (`resolution_core.slot_of`)
HEDGE_LAST = 15 * 60 + 8 + 7 * 60


def hedge_table(I: dict, days: list[str], tv: float) -> list[hc.HedgeDay | None]:
    """Each development day's hedge (`hedge_cycle.bracket_pair`, the plain shared bracket -- no breakeven move, which
    P-16's walk carries and the operator's hedge does not): entered at the session's first offered mark of P-16's walk
    at 200 ticks (the cutoff and D-533's cut, read from the walk with every coin forced long), both legs on the bars,
    20 micros, the round turn the gate charges a micro (None: no offered mark)."""
    import atlas_a3 as A

    from propedge.data.orb_kit import params
    from propedge.execution.fills import FillModel

    cfg = I["L"]["cfg"]
    tick = float(cfg["contract"]["tick"])
    slip = float(cfg["slip_ticks"]) * tick
    marks = _first_marks(_forced_walk(I, +1))
    q = params("NQ")
    fee = float(FillModel.load("assumed").round_turn_by_instrument[q["micro"]])
    arrays = A.bar_arrays(cfg, sorted(days))
    out: list[hc.HedgeDay | None] = []
    for d in days:
        if d not in marks.index:
            out.append(None)
            continue
        o, h, l, c = ([None if not np.isfinite(x) else float(x) for x in v] for v in arrays(d))
        t = int(marks.loc[d, "entry_t"]) - 1                      # the walk enters at the first bar after t
        out.append(hc.bracket_pair(o, h, l, c, t, stop=hc.HEDGE_STOP_TICKS * tick, slip=slip,
                                   last=min(HEDGE_LAST, len(o) - 1), micros=hc.HEDGE_MICROS,
                                   point_value=float(tv) / tick, fee_rt=fee))
    return out


def survivor_table(t: pd.DataFrame, days: list[str], tv: float, shift_r: float = 0.0) -> np.ndarray:
    """Each development day's first offered P-16 trade at R = 1, in dollars a micro (NaN: no trade), its R shifted by
    `shift_r` (the bound arm)."""
    first = _first_marks(t)
    per = float(t["stop_ticks"].iloc[0]) * float(tv)
    return np.array([(float(first.loc[d, "r_1"]) + shift_r) * per if d in first.index else np.nan for d in days])


def inputs() -> dict[str, Any]:
    import a3_brk30 as B
    import atlas_a3 as A
    import customer_slices as cs
    import rc150_dev_test as P16
    import rc150_firm_split as FS
    import rc_dev_test as D
    import score_fv3_grid as gf

    from propedge.campaign.gate import shifted_blocks

    I, b = P16.build_cells()
    t = b["cells"][P16.CELL]["trades"]
    if t is None or D.trades_hash(t) != P16.TRADES_SHA256:
        raise SystemExit("REFUSED (D-619): the cell is not P-16's (content hash).")
    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    days = [str(d) for d in b["days"]]
    keys = B.rrs(t)
    _, e_by, lb_by, _, _ = A.bounds(t, days, keys, cfg)
    cell, n1 = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    if n1 != len(t):
        raise SystemExit("REFUSED (D-619): the blocks hold a different number of trades.")
    cap = B.capacity(t, fcfg)
    fr = float(fcfg["state_policy"]["fresh"]["funded_rr"])
    import rc_screen as S

    kw = A.gate_kwargs(cell, fcfg, tv, I["plan"], e_by, lb_by, None, seed=P16.SEED, n_paths=N_PATHS, horizon=HORIZON,
                       capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=S.STRICT_GAP, purchase_budget=S.BUDGET)
    kw.pop("blocks")
    args = cs.engine_args(kw, "point", cell, purchase_budget=S.BUDGET)
    camp = hh.setup_from_engine_args(args, funded_horizon_days=HORIZON, combine_max_days=2000)
    p = camp.path
    if (int(p["max_concurrent_accounts"]), int(p["max_total_accounts"] or 0), tuple(p.get("purchase_budget") or ())) \
            != (5, 5, BUDGET):
        raise SystemExit("REFUSED (D-619): P-16's engine call is not five seats with the 20-in-21 budget.")
    delta_by_rr = {float(k): float(lb_by[k]) - float(e_by[k]) for k in e_by}
    blocks = {"point": cell, "lower_bound": shifted_blocks(cell, float(lb_by[fr]) - float(e_by[fr]), delta_by_rr)}
    setups = {"topstep": camp, "lucid": FS.lucid_setup(camp), "static": static_setup(camp)}
    print("the hedge table (P-16's walk at 200 ticks, long and short)...", flush=True)
    hedge = hedge_table(I, days, tv)
    surv = {"point": survivor_table(t, days, tv), "lower_bound": survivor_table(t, days, tv, delta_by_rr[1.0])}
    first = _first_marks(t)
    wins = first.loc[first["o_1"] == "t", "r_1"].to_numpy(float) * float(t["stop_ticks"].iloc[0]) * tv
    return {"I": I, "t": t, "days": days, "blocks": blocks, "setups": setups, "hedge": hedge, "surv": surv,
            "wins_per_micro": wins, "camp": camp, "delta_by_rr": delta_by_rr, "tv": tv}


def firm_model(X: dict, kind: str) -> hc.FirmModel:
    from propedge.campaign.lockstep import DEFAULT_PAYOUT_TIMING, FundedAccount

    s = X["setups"][kind]
    p = s.path
    rules = p["rules"]
    return hc.FirmModel(name=kind, rules=rules, policy=hc.survivor_policy(s.protocol), cap=float(rules.std_cap),
                        funded_cls=p.get("funded_account_cls") or FundedAccount,
                        payout_timing=p.get("payout_timing") or DEFAULT_PAYOUT_TIMING,
                        lag_days=int(p["payout_lag_days"]), activation=float(p["activation"]),
                        micros=hc.survivor_micros(X["wins_per_micro"], float(rules.std_winning_day_min)))


# ------------------------------------------------------------------------------------------------ 2. the identity


def _identity_task(task: tuple) -> list[dict]:
    import warnings

    warnings.filterwarnings("ignore")
    shift, blocks, setup, items = task
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=HORIZON) for _, s in items]
    jps = hh.run_joint(specs, setup, n_firms=1, mode=hh.UNHEDGED, doubled=False, firm_setups=[setup])
    return [{"shift": shift, "path": int(i), "final_cash": float(jp.paths[0].path.final_cash),
             "fees": float(jp.paths[0].path.total_fees), "payouts": float(jp.paths[0].path.total_payouts)}
            for (i, s), jp in zip(items, jps)]


def identity(X: dict, n: int, rd: Path) -> list[dict]:
    import rc150_dev_test as P16

    from propedge.campaign.lockstep import path_seeds

    ref = pd.read_csv(rd / "rc_s150_all_gate_paths.csv", float_precision="round_trip", low_memory=False)
    ref = ref[(ref["run"] == "gate") & np.isclose(ref["enforcement_p"].astype(float), 0.0)]
    items = list(enumerate(path_seeds(int(P16.SEED), int(n))))
    rows = []
    for shift in SHIFTS:
        got = _identity_task((shift, X["blocks"][shift], X["setups"]["topstep"], items))
        for g in got:
            r = ref[(ref["shift"] == shift) & (ref["path"].astype(int) == g["path"])]
            if len(r) != 1:
                raise SystemExit(f"REFUSED (D-619): the registered file holds {len(r)} rows for {shift} path {g['path']}.")
            r = r.iloc[0]
            ok = all(abs(float(g[c]) - float(r[c])) <= 1e-6 * max(1.0, abs(float(r[c])))
                     for c in ("final_cash", "fees", "payouts"))
            rows.append({"section": "identity", "check": f"P-16's gate path {g['path']} at {shift} (final cash, fees, "
                                                         "payouts) through the episode runner", "holds": bool(ok),
                         "shift": shift, "path": g["path"]})
    return rows


# ------------------------------------------------------------------------------------------------ 3. the libraries


def _episode_task(task: tuple) -> list[dict]:
    import warnings

    warnings.filterwarnings("ignore")
    kind, seats, shift, blocks, setup, seeds = task
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=EPISODE_HORIZON) for s in seeds]
    jps = hh.run_joint(specs, setup, n_firms=1, mode=hh.UNHEDGED, doubled=False, firm_setups=[setup])
    out = []
    for jp in jps:
        e = hc.episode_of(jp.paths[0], float(setup.path["initial_bankroll"]))
        out.append({"pass_day": e.pass_day, "fees": e.fees.tolist(), "purchase_days": list(e.purchase_days)})
    return out


def _pool(tasks: list[tuple], fn, workers: int, what: str) -> list:
    import customer_journey as CJ

    return CJ._pool_run(tasks, fn, workers, what)


def libraries(X: dict, n: int, workers: int) -> dict[tuple, list[hc.Episode]]:
    tasks, keys = [], []
    for ki, kind in enumerate(KINDS):
        for seats in SEATS:
            setup = hh.with_seats(X["setups"][kind], seats, BUDGET)
            for si, shift in enumerate(SHIFTS):
                rng = np.random.default_rng([SEED, ki, seats, si])
                seeds = [int(rng.integers(0, 2**31 - 1)) for _ in range(int(n))]
                for j in range(0, len(seeds), EPISODE_CHUNK):
                    tasks.append((kind, seats, shift, X["blocks"][shift], setup, seeds[j:j + EPISODE_CHUNK]))
                    keys.append((kind, seats, shift))
    res = _pool(tasks, _episode_task, workers, "evaluation episodes")
    out: dict[tuple, list[hc.Episode]] = {}
    for k, chunk in zip(keys, res):
        out.setdefault(k, []).extend(hc.Episode(None if e["pass_day"] is None else int(e["pass_day"]),
                                                np.asarray(e["fees"], float), tuple(e["purchase_days"])) for e in chunk)
    return out


def episode_rows(libs: dict[tuple, list[hc.Episode]]) -> list[dict]:
    rows = []
    for (kind, seats, shift), eps in sorted(libs.items()):
        passed = [e for e in eps if e.pass_day is not None]
        rows.append({"section": "episodes", "firm": kind, "seats": seats, "shift": shift, "episodes": len(eps),
                     "share_passed": len(passed) / len(eps),
                     "days_to_pass_p50": float(np.median([e.pass_day for e in passed])) if passed else np.nan,
                     "days_to_pass_p90": float(np.percentile([e.pass_day for e in passed], 90)) if passed else np.nan,
                     "evaluations_per_pass_mean": float(np.mean([len(e.purchase_days) for e in passed])) if passed else np.nan,
                     "fees_to_pass_mean": float(np.mean([e.fees.sum() for e in passed])) if passed else np.nan,
                     "fees_to_pass_p90": float(np.percentile([e.fees.sum() for e in passed], 90)) if passed else np.nan})
    return rows


# ------------------------------------------------------------------------------------------------ 4. the cycles


def _cycle_task(task: tuple) -> list[dict]:
    second, seats, shift, firms, libs, hedge, surv, items = task
    out = []
    for i, s in items:
        r = hc.simulate_path(seed=int(s), horizon=HORIZON, firms=firms, libraries=libs, hedge_days=hedge,
                             survivor_per_micro=surv)
        r.update({"second": second, "seats": seats, "shift": shift, "path": int(i), "seed": int(s)})
        out.append(r)
    return out


def cycles(X: dict, libs: dict, models: dict, n_paths: int, workers: int) -> dict[tuple, list[dict]]:
    from propedge.campaign.lockstep import path_seeds

    items = list(enumerate(path_seeds(SEED, int(n_paths))))
    tasks, keys = [], []
    for second in SECOND:
        for seats in SEATS:
            for shift in SHIFTS:
                firms = (models["topstep"], models[second])
                lb = (libs[("topstep", seats, shift)], libs[(second, seats, shift)])
                for j in range(0, len(items), CYCLE_CHUNK):
                    tasks.append((second, seats, shift, firms, lb, X["hedge"], X["surv"][shift], items[j:j + CYCLE_CHUNK]))
                    keys.append((second, seats, shift))
    res = _pool(tasks, _cycle_task, workers, "cycles")
    out: dict[tuple, list[dict]] = {}
    for k, chunk in zip(keys, res):
        out.setdefault(k, []).extend(chunk)
    return out


def path_rows(recs: list[dict]) -> list[dict]:
    rows = []
    for r in recs:
        c = np.cumsum(np.asarray(r["flows"], float))
        pays = sorted(int(d) for d in r["payout_days"])
        until = pays[0] if pays else len(c) - 1
        rows.append({"label": hc.TAG, "second": r["second"], "seats": r["seats"], "shift": r["shift"], "path": r["path"],
                     "seed": r["seed"], "payouts": len(pays), "first_payout_day": pays[0] if pays else np.nan,
                     "upfront_to_first_payout": max(0.0, -float(c[:until + 1].min())) + MARGIN,
                     "required": max(0.0, -float(c.min())) + MARGIN, "net": float(c[-1]), "fees": float(r["fees"]),
                     "payout_net": float(sum(r["payout_nets"])), "evaluations": int(r["evaluations"]),
                     "funded_lost": int(r["funded_lost"]), "cycles_started": int(r["cycles_started"]),
                     "hedge_flat_sessions": int(r["hedge_flat_sessions"]),
                     "survivor_breaches": int(r["survivor_breaches"])})
    return rows


def table_rows(X: dict, models: dict) -> list[dict]:
    h = [x for x in X["hedge"] if x is not None]
    w = [hc.hedge_winner(x.long_kind, x.short_kind) for x in h]
    rows = [{"section": "tables", "table": "hedge", "days": len(X["hedge"]), "days_with_mark": len(h),
             "share_long_wins": float(np.mean([x == "long" for x in w])),
             "share_short_wins": float(np.mean([x == "short" for x in w])),
             "share_flat": float(np.mean([x is None for x in w])),
             "winner_pnl_mean": float(np.mean([(x.long_pnl if y == "long" else x.short_pnl) for x, y in zip(h, w) if y])),
             "loser_pnl_mean": float(np.mean([(x.short_pnl if y == "long" else x.long_pnl) for x, y in zip(h, w) if y]))}]
    for shift in SHIFTS:
        s = X["surv"][shift]
        f = s[np.isfinite(s)]
        rows.append({"section": "tables", "table": "survivor", "shift": shift, "days": len(s), "days_with_mark": len(f),
                     "share_wins": float(np.mean(f > 0)), "per_micro_win_median": float(np.median(f[f > 0])),
                     "per_micro_loss_median": float(np.median(f[f < 0]))})
    for kind, m in models.items():
        rows.append({"section": "tables", "table": "firm", "firm": kind, "survivor_micros": m.micros,
                     "winning_day_min": float(m.rules.std_winning_day_min), "winning_days": int(m.rules.std_winning_days),
                     "payout_cap": m.cap, "payout_frac": float(m.rules.payout_max_frac_of_balance),
                     "profit_split": float(m.rules.profit_split), "activation": m.activation, "lag_days": m.lag_days,
                     "funded_class": m.funded_cls.__name__})
    return rows


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="the identity at 2 paths, tiny libraries and cycles; nothing written")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t0 = time.time()
    n_id, n_ep, n_paths = (2, 3, 4) if a.check else (IDENTITY_PATHS, N_EPISODES, N_PATHS)
    X = inputs()
    ids = identity(X, n_id, rd)
    bad = [r for r in ids if not r["holds"]]
    if bad:
        print("REFUSED (D-619): the identity fails -- " + "; ".join(r["check"] for r in bad))
        return 3
    print(f"identity HOLDS: P-16's first {n_id} gate paths at both shifts through the episode runner", flush=True)
    models = {k: firm_model(X, k) for k in KINDS}
    print("the evaluation libraries...", flush=True)
    libs = libraries(X, n_ep, a.workers)
    print(f"the cycles ({len(SECOND) * len(SEATS)} cells x {len(SHIFTS)} arms, {n_paths} paths)...", flush=True)
    recs = cycles(X, libs, models, n_paths, a.workers)
    cells = []
    for second in SECOND:
        for seats in SEATS:
            for shift in SHIFTS:
                rd_ = hc.readings(recs[(second, seats, shift)], horizon=HORIZON, margin=MARGIN)
                cells.append({"section": "cell", "second": second, "seats": seats, "shift": shift, **rd_})
    bound = [c for c in cells if c["shift"] == "lower_bound"]
    rk = hc.ranking(bound, tolerance=TOLERANCE)
    for i, c in enumerate(bound):
        c["within_tolerance"] = i in rk["within_tolerance"]
        c["on_frontier"] = i in rk["frontier"]
        c["named"] = i == rk["named"]
    nm = bound[rk["named"]]
    secs = time.time() - t0
    if a.check:
        print(f"every identity holds; {len(cells)} cell-arms ran at {n_paths} paths on {n_ep}-episode libraries; nothing "
              f"written, no reading printed (--check). {secs:.0f} s")
        return 0
    rank_row = {"section": "ranking", "rule": "D-619 (7): of the cells within 10 % of the smallest p90 gap between "
                                              "payouts (bound arm), the smallest p90 upfront bankroll to the first payout",
                "best_gap_p90": rk["best_gap_p90"], "named_second": nm["second"], "named_seats": nm["seats"],
                "frontier": "; ".join(f"{bound[i]['second']} {bound[i]['seats']}" for i in rk["frontier"])}
    res = pd.DataFrame(ids + table_rows(X, models) + episode_rows(libs) + cells + [rank_row])
    res.insert(0, "label", hc.TAG)
    hc_rows = res.to_dict("records")
    hh.require_label(hc_rows)
    paths = pd.DataFrame([row for k in sorted(recs) for row in path_rows(recs[k])])
    params = {"decision": DECISION, "seed": SEED, "n_paths": n_paths, "horizon": HORIZON,
              "episode_horizon": EPISODE_HORIZON, "n_episodes": n_ep, "seats": list(SEATS), "second": list(SECOND),
              "budget": list(BUDGET), "tolerance": TOLERANCE, "margin": MARGIN, "identity_paths": n_id,
              "hedge": {"micros": hc.HEDGE_MICROS, "stop_ticks": hc.HEDGE_STOP_TICKS, "rr": 1.0,
                        "entry": "the session's first offered mark of P-16's walk at the stop"},
              "survivor": "the session's first offered P-16 trade at R = 1, at the smallest whole-micro size whose "
                          "median winning trade nets the firm's winning-day minimum; one payout, then retired",
              "static": {"floor": "start - $2,000 fixed (evaluation and funded)", "check": "the close (settlement legacy)",
                         "green_days_to_pass": hc.GREEN_DAYS, "green_day_min": hc.GREEN_DAY_MIN},
              "lucid": "rc150_firm_split.lucid_setup (D-575): two unverified fee rows uncharged -- an upper bound",
              "approximation": "each firm's evaluation phase drawn independently from its episode library (D-619 (4))",
              "trades_sha256": __import__("rc_dev_test").trades_hash(X["t"]), "seconds": round(secs, 1),
              "workers": int(a.workers)}
    notes = {"status": "EXPLORATORY, HYPOTHETICAL (D-619): hypothetical_hedge -- prohibited conduct (Topstep 13747047, "
                       "Lucid 11404734), never a candidate; the ranking is D-619 (7)'s, declared before reading",
             "label": hc.LABEL}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(SECOND) * len(SEATS), parameters=params, notes=notes,
                 description="EXPLORATORY, HYPOTHETICAL (D-619): the hedge cycle on P-16's executions -- evaluations at "
                             "two firms, one full-port funded hedge, the survivor's flip days to one payout -- by second "
                             "firm (Lucid, static EOD, Topstep) and seats (1-5), at the point and the 0.05 bound.")
    write_result(paths, f"{RESULT}_paths", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(SECOND) * len(SEATS), parameters=params, notes=notes,
                 description="EXPLORATORY, HYPOTHETICAL (D-619): the hedge cycle's per-path record (every cell, arm and "
                             "path).")
    counter = VariantCounter(path=rd / "variants.jsonl")
    for second in SECOND:
        for seats in SEATS:
            counter.record(prereg_id=hc.VARIANT_FAMILY, seed=SEED, exploratory=True,
                           params={"study": "D-619's hedge cycle on P-16's executions", "second_firm": second,
                                   "seats": seats, "paths": n_paths, "episodes": n_ep},
                           label=f"D-619's hedge cycle: Topstep + {second}, {seats} seat(s) -- {hc.TAG}")
    print(f"written: {RESULT}.csv and {RESULT}_paths.csv ({secs:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
