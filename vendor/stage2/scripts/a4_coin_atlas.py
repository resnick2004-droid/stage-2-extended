"""EXPLORATORY (D-550): family A4 -- the coin-benchmarked strategy atlas. Every strategy on the declared menu is measured
by its per-trade lift over its own coin twin, and survives only if that lift beats the luck of the whole search
(a family-wise max-statistic bootstrap); survivors alone go to P-16's engine call against the coin plan.

    python scripts/a4_coin_atlas.py --check --days 40 --reps 200        # a smoke on the first days; nothing written
    python scripts/a4_coin_atlas.py --workers 2                         # the reading (from a clean checkout, D-474)

**Order (D-550):** (1) the menu is built and every pattern the atlas code cannot build is dropped and listed -- before
any bar is walked; (2) every development day of NQ (2020-01-01 .. 2026-07-16, `propedge.data.bars` through the windows
guard) on A1's day kinds -- FOMC days ('o'), early closes and empty days walk nothing; a report day ('b') offers no event
before 07:35 CT (D-533) -- has each pattern's events found by `atlas_core.a_events` (the kits' code, A1's decision window
17:00 to 14:00 CT, the prior regular session's range carried for `pdhl` as `atlas_walk.walk_days` carries it), and
each event minute walked long and short by FV3-C's rung walk (`fv3_rung_walk.day_walks`) at both stops and the
table's offered R, at entry delays 0 and 5, settled in R by FV3's scheme (`atlas_a3.cell_trades`' arithmetic: a tick at
entry, the fee per micro-equivalent at the fresh Combine's size, the exit's ticks by kind); (3) each event's lift, per
offered R, is accumulated per day and strategy (`a4_coin_atlas.lift`); (4) the stationary block bootstrap's
max-statistic test over every strategy and R (`a4_coin_atlas.maxstat_test`), BH beside; (5) only for survivors: P-14's
identity first (`rc_screen.identity_problems`), then each surviving strategy -- its events on its winning side at its
stop and delay, every R of the grid -- through P-16's engine call (`rc_screen.Runner`: the no-closure table, the
budget, the strict rule, re-entry when flat) at the screen's seed, 500 paths, with its zero-edge twin, beside the coin
cell at the same stop read from `results/rc_width_screen.csv` (never rerun).

Written: `results/a4_coin_atlas.csv` (sections menu, lift, bootstrap, survivors, campaign), EXPLORATORY, one variant
per strategy under `D-550:a4_coin_atlas`.
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

from propedge.research import a4_coin_atlas as A4  # noqa: E402

SCRIPT = "scripts/a4_coin_atlas.py"
DECISION = A4.DECISION
RESULT = "a4_coin_atlas"
FAMILY_ID = f"{DECISION}:a4_coin_atlas"
N_PATHS = 500
WIDTH_FILE = "rc_width_screen.csv"         # the coin cells at the screen's seed (D-542), read beside
COIN_ROW = {100: ("reference", "rc_s100_all_nr"), 150: ("cell", "rc_s150_all")}
READING = "EXPLORATORY (D-550): the coin-benchmarked strategy atlas; a family-wise test; selects nothing beyond D-550 (5)"


# ------------------------------------------------------------------------------------------------ the walk


def _lists(a: np.ndarray) -> list:
    return [None if not np.isfinite(x) else float(x) for x in a]


def scan(I: dict[str, Any], patterns: list[dict], *, days_limit: int | None = None, keep: dict | None = None
         ) -> dict[str, Any]:
    """Walk every day once: the accumulators per (day, hypothesis) and, for `keep` = {(pattern index, stop, delay):
    side sign}, the kept strategies' events (for their campaign trades). Returns day_sum, day_n, sums for context."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge.outcomes import atlas_core
    from propedge.outcomes.collect_core import C_FLAT, c_slot
    from propedge.research import fv3_rung_walk as RW

    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    offered = tuple(sorted(float(R) for R in zd.policy_rrs(I["plan"])))
    if offered != tuple(float(x) for x in A4.OFFERED_R):
        raise SystemExit(f"REFUSED ({DECISION}): the table offers R {offered}, not D-550's {A4.OFFERED_R}.")
    days = L["days"].copy()
    days["date"] = days["date"].astype(str)
    days = days.sort_values("date").reset_index(drop=True)
    if days_limit is not None:
        days = days.head(int(days_limit))
    walked = days[days["day_kind"].astype(str).isin(("n", "b"))]["date"].tolist()
    wix = {d: i for i, d in enumerate(walked)}
    first = A4._clock(cfg["day"]["first_decision_ct"])
    lh, lm = (int(x) for x in str(cfg["day"]["last_decision_ct"]).split(":"))
    last = int(c_slot(lh, lm))
    clear = int(c_slot(7, 35))
    tick, entry_ticks = float(cfg["contract"]["tick"]), float(cfg["slip_ticks"])
    fees = A.fee_by_stop(fcfg, A4.STOPS, tv)
    bl = RW.brackets(A4.STOPS, A4.OFFERED_R)
    nR = len(A4.OFFERED_R)
    strats = A4.strategies(patterns)
    sid = {(s["pattern_index"], s["stop_ticks"], s["delay"]): i for i, s in enumerate(strats)}
    H = len(strats) * nR
    day_sum = np.zeros((len(walked), H))
    day_n = np.zeros((len(walked), len(strats)))
    sq = np.zeros(H)
    side_r = np.zeros(H)
    flat = np.zeros(H)
    kept_rows: dict[tuple, list] = {k: [] for k in (keep or {})}
    arrays = A.bar_arrays(cfg, days["date"].tolist())
    P = {"patterns": [A4.to_core(p) for p in patterns], "first_slot": first, "last_slot": last, "prior": None}
    prior = None
    kinds = dict(zip(days["date"], days["day_kind"].astype(str)))
    for day in days["date"]:
        o, h, l, c = arrays(day)
        kind = kinds[day]
        if kind in ("n", "b"):
            lo, hi, lw, cl = _lists(o), _lists(h), _lists(l), _lists(c)
            P["prior"] = prior
            ev = atlas_core.a_events(lo, hi, lw, cl, P)
            if kind == "b":
                ev = [e for e in ev if int(e[1]) >= clear]
            if ev:
                ev_a = np.array(ev, dtype=np.int64)                       # (pattern, slot, side)
                slots = sorted({int(x) for x in ev_a[:, 1]})
                di = wix[day]
                for d in A4.DELAYS:
                    ent, res = RW.day_walks(o, h, l, c, slots, int(d), tick, bl)
                    if not ent:
                        continue
                    row = {(int(s), int(sd)): i for i, (s, sd, _) in enumerate(ent)}
                    kinds_m = np.asarray(res["kind"])
                    gross = np.asarray(res["gross"], float)
                    net = np.empty_like(gross)
                    for b, (S, _R, _T) in enumerate(bl):
                        net[:, b] = A4.net_r(gross[:, b], kinds_m[:, b], S, fees[int(S)], tick_value=tv,
                                             entry_ticks=entry_ticks)
                    a_rows, o_rows, pids, signs = [], [], [], []
                    for pid, t, sd in ev:
                        i, j = row.get((int(t), int(sd))), row.get((int(t), -int(sd)))
                        if i is None or j is None:
                            continue
                        a_rows.append(i)
                        o_rows.append(j)
                        pids.append(int(pid))
                        signs.append(int(sd))
                    if not a_rows:
                        continue
                    a_rows_a, o_rows_a = np.array(a_rows), np.array(o_rows)
                    lf = A4.lift(net[a_rows_a], net[o_rows_a])                  # (E, stops x R)
                    for si, S in enumerate(A4.STOPS):
                        cols = slice(si * nR, (si + 1) * nR)
                        st = np.array([sid[(p, int(S), int(d))] for p in pids])
                        hcols = (st[:, None] * nR + np.arange(nR)[None, :])
                        np.add.at(day_sum[di], hcols.ravel(), lf[:, cols].ravel())
                        np.add.at(sq, hcols.ravel(), (lf[:, cols] ** 2).ravel())
                        np.add.at(side_r, hcols.ravel(), net[a_rows_a][:, cols].ravel())
                        np.add.at(flat, hcols.ravel(), (kinds_m[a_rows_a][:, cols] == RW.FLATTEN).ravel().astype(float))
                        np.add.at(day_n[di], st, 1.0)
                    if keep:
                        for (pid, t, sd) in ev:
                            for k, sign in keep.items():
                                if k[0] == int(pid) and int(k[2]) == int(d):
                                    side = int(sd) * int(sign)
                                    if (int(t), side) in row:
                                        kept_rows[k].append((day, int(t), side))
        if kind != "x":
            rng = atlas_core.a_rth_range(_lists(o), _lists(h), _lists(l), A4._clock("08:30"), C_FLAT)
            if rng is not None:
                prior = rng
    return {"strats": strats, "walked": walked, "day_sum": day_sum, "day_n": day_n, "sq": sq, "side_r": side_r,
            "flat": flat, "kept": kept_rows, "days": days["date"].tolist(), "kinds": kinds}


# ------------------------------------------------------------------------------------------------ survivors' trades


def survivor_trades(I: dict[str, Any], picks: list[tuple[str, int, int]], stop: int, delay: int) -> pd.DataFrame:
    """A survivor's trades in FV3-C's gate-trades shape: its events `picks` [(date, slot, side)] walked by the rung walk
    at its stop and delay at every R of the grid, settled as `resolved_coin.cell_trades` settles them."""
    import atlas_a3 as A
    import zero_edge_decomposition as zd

    from propedge.research import fv3_rung_walk as RW
    from propedge.research import resolved_coin as rc

    L = I["L"]
    cfg, fcfg, tv = L["cfg"], L["fcfg"], float(L["tv"])
    rr_grid = A.rrs(cfg)
    by_day: dict[str, list[tuple[int, int]]] = {}
    for d, t, s in picks:
        by_day.setdefault(str(d), []).append((int(t), int(s)))
    mins = pd.DataFrame([{"date": d, "slot": t} for d, v in by_day.items() for t in sorted({x for x, _ in v})])
    arr = A.bar_arrays(cfg, sorted(by_day))
    w = A.walk_minutes(mins, arr, int(delay), float(cfg["contract"]["tick"]), (int(stop),), rr_grid)
    want = {(d, t, s) for d, v in by_day.items() for t, s in v}
    w = w[[(str(a), int(b), int(c)) in want for a, b, c in zip(w["date"], w["slot"], w["side"])]].copy()
    kinds = dict(zip(L["days"]["date"].astype(str), L["days"]["day_kind"].astype(str)))
    fees = A.fee_by_stop(fcfg, (int(stop),), tv)
    coins = {(str(d), int(t)): int(s) for d, t, s in zip(w["date"], w["slot"], w["side"])}
    t = rc.cell_trades(w, kinds, sorted({int(x) for x in w["slot"]}), int(stop), coins, fees, rr_grid=rr_grid,
                       fresh_rr=float(fcfg["state_policy"]["fresh"]["combine_rr"]), tick_value=tv,
                       entry_ticks=float(cfg["slip_ticks"]), cut=0)
    return zd.pad(t, sorted(set(float(R) for R in rr_grid) | set(zd.policy_rrs(I["plan"]))))


def coin_row(rd: Path, stop: int) -> dict[str, Any]:
    from propedge.reporting.results import read_result

    sec, cell = COIN_ROW[int(stop)]
    w = read_result(rd / WIDTH_FILE)
    r = w[(w["section"].astype(str) == sec) & (w["cell"].astype(str) == cell)]
    if len(r) != 1:
        raise SystemExit(f"REFUSED ({DECISION}): {WIDTH_FILE} has {len(r)} {sec} rows for {cell}, not one.")
    return r.iloc[0].to_dict()


# ------------------------------------------------------------------------------------------------ the study


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    import rc_screen as S

    from propedge import RESULTS_DIR
    from propedge.backtest.harness import VariantCounter
    from propedge.outcomes.collect_core import c_slot
    from propedge.reporting.results import write_result

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="a smoke: nothing written, no lift printed")
    ap.add_argument("--days", type=int, default=None, help="with --check: the first N development days")
    ap.add_argument("--reps", type=int, default=A4.BOOT_REPS, help="with --check: bootstrap replicates")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=N_PATHS)
    ap.add_argument("--campaign-check", action="store_true",
                    help="with --check: run the first strategy through the campaign at --paths (timing seam)")
    a = ap.parse_args(argv)
    if not a.check and (a.days is not None or int(a.reps) != A4.BOOT_REPS or int(a.paths) != N_PATHS
                        or a.campaign_check):
        print(f"REFUSED ({DECISION}): the reading runs every day, {A4.BOOT_REPS} replicates and {N_PATHS} paths; a "
              "smaller run is --check (writes nothing).")
        return 2
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    # (1) the menu, before any bar
    I = S.inputs()
    cfg = I["L"]["cfg"]
    lh, lm = (int(x) for x in str(cfg["day"]["last_decision_ct"]).split(":"))
    patterns, menu_rows = A4.build_menu(A4._clock(cfg["day"]["first_decision_ct"]), int(c_slot(lh, lm)))
    dropped = [r for r in menu_rows if not r["buildable"]]
    print(f"the menu: {len(menu_rows)} patterns declared, {len(patterns)} built, {len(dropped)} dropped "
          f"{[r['pattern'] for r in dropped]}; {len(A4.strategies(patterns))} strategies", flush=True)
    # (2)-(3) the walk and the lift
    t0 = time.time()
    sc = scan(I, patterns, days_limit=a.days)
    strats = sc["strats"]
    hyp = A4.hypothesis_frame(strats)
    nR = len(A4.OFFERED_R)
    n_trades = np.repeat(sc["day_n"].sum(axis=0), nR)
    print(f"the walk: {len(sc['walked'])} walked days of {len(sc['days'])}, {int(sc['day_n'].sum())} strategy trades, "
          f"{time.time() - t0:.0f} s", flush=True)
    # (4) the noise guard
    t1 = time.time()
    counts = A4.stationary_counts(len(sc["walked"]), reps=int(a.reps))
    day_n_h = np.repeat(sc["day_n"], nR, axis=1)
    test = A4.maxstat_test(sc["day_sum"], day_n_h, counts)
    bh = A4.benjamini_hochberg(test["p"])
    print(f"the bootstrap: {int(a.reps)} replicates over {len(sc['walked'])} days and {len(hyp)} hypotheses, "
          f"{time.time() - t1:.0f} s", flush=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = test["mean"]
        sd_trade = np.sqrt(np.maximum(sc["sq"] / np.where(n_trades > 0, n_trades, np.nan) - mean ** 2, 0.0))
        t_naive = mean / (sd_trade / np.sqrt(np.where(n_trades > 1, n_trades, np.nan)))
    hyp = hyp.assign(trades=n_trades, mean_lift=mean, sd_lift_trade=sd_trade, t_iid=t_naive,
                     sd_boot=test["sd"], t_boot=test["t"], p_boot=test["p"], bh_reject=bh,
                     survives=test["survives"], winning_side=np.where(mean > 0, "follow", "fade"),
                     mean_r_follow=sc["side_r"] / np.where(n_trades > 0, n_trades, np.nan),
                     unresolved_follow=sc["flat"] / np.where(n_trades > 0, n_trades, np.nan))
    surv = hyp[hyp["survives"].astype(bool)]
    if a.check:
        print(f"menu, walk and bootstrap ran; {len(surv)} hypotheses past the critical value at this smoke's size "
              "(not a reading); nothing written.", flush=True)
    # (5) survivors only
    camp_rows: list[dict] = []
    run_these = surv.drop_duplicates("strategy")
    if a.check:                            # a smoke's "survivors" mean nothing (too few days): no campaign unless asked
        run_these = hyp.drop_duplicates("strategy").head(1) if a.campaign_check else run_these.iloc[0:0]
    if len(run_these):
        R = S.Runner(I, a.workers)
        bad = S.identity_problems(R, a.paths)
        if bad:
            print(f"REFUSED ({DECISION}): P-14's trades are not {S.P14_PATHS} -- " + "; ".join(bad[:8]))
            return 3
        print(f"identity HOLDS: P-14's trades = the first {a.paths} paths of {S.P14_PATHS}", flush=True)
        keep = {}
        for _, r in run_these.iterrows():
            keep[(int(r["pattern_index"]), int(r["stop_ticks"]), int(r["delay"]))] = 1 if r["winning_side"] == "follow" else -1
        sc2 = scan(I, patterns, days_limit=a.days, keep=keep)
        days_all = sorted(sc2["days"])
        for _, r in run_these.iterrows():
            k = (int(r["pattern_index"]), int(r["stop_ticks"]), int(r["delay"]))
            picks = sc2["kept"][k]
            t = survivor_trades(I, picks, int(r["stop_ticks"]), int(r["delay"]))
            label = f"{r['strategy']}_{r['winning_side']}"
            df = R.run(label, t, days_all, a.paths)
            tw = R.run(f"{label} twin", t, days_all, a.paths, twin=True)
            if a.check:
                print(f"  {label}: {len(t)} candidates ran at {a.paths} paths (cell and twin) -- no growth printed",
                      flush=True)
                continue
            g = lambda x, s, col="pf_growth_on_base_p50": float(x[(x["shift"] == s) & (x["enforcement_p"] == 0)][col].iloc[0])  # noqa: E731
            coin = coin_row(rd, int(r["stop_ticks"]))
            camp_rows.append({"section": "campaign", "strategy": r["strategy"], "side_rule": r["winning_side"],
                              "stop_ticks": int(r["stop_ticks"]), "delay": int(r["delay"]), "candidates": int(len(t)),
                              "growth_on_required": g(df, "lower_bound"), "growth_on_required_point": g(df, "point"),
                              "required_p90": g(df, "lower_bound", "pf_required_p90"),
                              "growth_zero_edge_twin": g(tw, "point"),
                              "coin_cell": COIN_ROW[int(r["stop_ticks"])][1],
                              "coin_growth_on_required": float(coin["growth_on_required"]),
                              "growth_minus_coin": g(df, "lower_bound") - float(coin["growth_on_required"]),
                              "beats_coin_plan": bool(g(df, "lower_bound") > float(coin["growth_on_required"]))})
    secs = time.time() - t_all
    if a.check:
        print(f"--check done in {secs:.0f} s; nothing written.")
        return 0
    boot_row = {"section": "bootstrap", "reps": int(a.reps), "mean_block": A4.BOOT_BLOCK, "seed": A4.BOOT_SEED,
                "statistic": "studentised mean lift (mean / bootstrap sd), two-sided max over every strategy and R",
                "fwer": A4.FWER, "critical_t": test["crit"], "hypotheses": int(len(hyp)),
                "walked_days": int(len(sc["walked"])), "survivors": int(len(surv)),
                "survivor_strategies": int(surv["strategy"].nunique()), "bh_rejections": int(bh.sum()),
                **{f"max_abs_t_{k}": v for k, v in test["max_quantiles"].items()}}
    res = pd.concat([pd.DataFrame([{"section": "menu", **{k: (str(v) if k == "params" else v) for k, v in m.items()}}
                                   for m in menu_rows]),
                     hyp.assign(section="lift"), pd.DataFrame([boot_row]), surv.assign(section="survivors"),
                     pd.DataFrame(camp_rows)], ignore_index=True)
    res.insert(1, "reading", READING)
    counter = VariantCounter(path=rd / "variants.jsonl")
    for s in strats:
        counter.record(prereg_id=FAMILY_ID, seed=A4.BOOT_SEED, exploratory=True,
                       params={"study": "A4 coin-benchmarked atlas (D-550)", "strategy": s["strategy"],
                               "pattern": s["pattern"], "stop_ticks": s["stop_ticks"], "delay": s["delay"]},
                       label=f"D-550's A4: {s['strategy']} (lift over its coin twin)")
    write_result(res, RESULT, script=SCRIPT, seed=A4.BOOT_SEED, exploratory=True, results_dir=results_dir,
                 variant_count=len(strats),
                 parameters={"decision": DECISION, "menu": [m["pattern"] for m in menu_rows],
                             "dropped": [m["pattern"] for m in dropped], "stops_ticks": list(A4.STOPS),
                             "delays": list(A4.DELAYS), "offered_r": list(A4.OFFERED_R), "reps": int(a.reps),
                             "mean_block": A4.BOOT_BLOCK, "boot_seed": A4.BOOT_SEED, "fwer": A4.FWER, "bh_q": A4.BH_Q,
                             "news": "FOMC days out; no report-day event before 07:35 CT (D-533)",
                             "campaign_seed": int(S.SEED), "n_paths": int(a.paths), "coin_file": WIDTH_FILE,
                             "workers": int(a.workers), "seconds": round(secs, 1)},
                 notes={"status": READING, "selection": "survivors of the family-wise test alone run the campaign; "
                        "BH is beside, never selecting"},
                 description="EXPLORATORY (D-550): 34 atlas patterns x 2 stops x 2 entry delays (136 strategies), each "
                             "trade's lift over its coin twin at every offered R, a stationary block bootstrap's "
                             "studentised max-statistic test family-wise at 5 % (BH at 10 % beside), and survivors "
                             "through P-16's engine call against the coin plan.")
    print(f"written: {RESULT}.csv ({len(surv)} surviving hypotheses, {len(camp_rows)} campaigns; {secs:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
