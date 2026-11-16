"""HYPOTHETICAL (D-514): the cross-firm hedge pair on P-14's design -- `hypothetical_hedge`, EXPLORATORY, NOT A CANDIDATE.

    python scripts/hypo_hedge_a3.py --identity             # the identities only (P-14's paths, D-508's slices)
    python scripts/hypo_hedge_a3.py --workers 4            # the study; writes results/hypo_hedge_a3.csv

Cross-firm and cross-account hedging are prohibited (Topstep 13747047 / 10296582, Lucid 11404734; tier 1, D-145) and
that does not change. The operator (2026-11-01): "I'm asking you to ignore the rules and model this hypothetically" --
does a hedge pair across two firms make passes and payouts more consistent, and at what cost? Every row, manifest and
variant is labelled `hypothetical_hedge`; nothing here is ranked, sized or carried into a protocol (D-514).

**The design** (D-514; `propedge.research.hypo_hedge` for the deal): two firms with Topstep's verified contract
(Firm H's convention, D-203), five seats each, one pooled wallet (D-206), each firm P-14's protocol exactly -- A3-BRK30's
trades on FV3-C's rungs, the no-closure v12 table (D-502), the purchase budget of 20 in 21 trading days, the strict
one-at-a-time rule PER FIRM (D-429), FV3-C's engine call through `atlas_a3.gate_kwargs` (the placement off, 0 %
denial; the conduct model's switches at nothing, so it applies no consequence). Each event of the cell is also walked
on the opposite side from the same bars (`a3_brk30.cell_trades(L, "fade")`, the A3 rung walk holds both sides).

* **(a) unhedged** -- each signal to one account at one firm (`two_firms.JointRouter`'s deal: never opposite across
  firms, the firm waiting longest, its longest-waiting account): P-14's design at ten seats;
* **(b) hedged** -- the same lead leg, and the other firm's account in the lead's slot on the opposite side, paired by
  slot as D-203; a signal one firm can take and the other cannot trades unhedged and is counted;
* **(c) hedged_combines** -- as (b) only when both legs are Combines; funded accounts trade unhedged.

Beside them, the **reference** `p14_one_firm`: one firm's five seats, the same deal -- P-14's configuration, which must
reproduce the first `IDENTITY_PATHS` paths of P-14's per-path record (section `gate`, point and bound, 0 %) at seed
20261131 or nothing runs; and its slices must equal D-508's `p13_noclose_b20` rows, start for start.

**Arms:** 500 paths at seed 20261131 (D-512's), 504 sessions; the point arm and the bound-shifted arm -- the cell's
trades at the 0.05 bound of e at each R (the gate row's shift) and the opposite walk moved the same amount the other way
(`hypo_hedge.mirror_shift`: one set of bars). **Readings per arm** (pooled over both firms; `hypo_hedge.readings`):
growth on the required bankroll and the required bankroll p90; the pass rate per Combine and, for the hedged arms, per
Combine pair (two Combines that traded as a pair: the share with a pass, both passing, passes per pair); the share of
paths with no pass (and no payout) in the first 21 and 63 sessions; the chance of no pass in N consecutive resolved
Combines (3, 5, 10, 20; empirical, in the order they resolved); the days between passes and between payouts (median,
p90, max) and the longest droughts; cost per pass (all fees over all passes); payouts per month; the deal's counts.
**Customer slices** (D-508's machinery: every start of the window in historical order, 21 / 63 / 126 sessions,
`customer_slices.summarise`), the bound-shifted (`verdict`) arm, pooled.

Writes `results/hypo_hedge_a3.csv` (sections `identity`, `arm`, `slices`), its per-path companion
`results/hypo_hedge_a3_paths.csv`, and the variants under `D-514:hypothetical_hedge` (one per arm).
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

SCRIPT = "scripts/hypo_hedge_a3.py"
DECISION = "D-514"
RESULT = "hypo_hedge_a3"
SEED = 20261131                            # D-512's campaign seed, P-14's
SLICE_SEED = 20261028                      # D-508's slice campaign's seed (`customer_slices.p13_campaign`); a replay draws nothing
N_PATHS = 500
HORIZONS = (21, 63, 126)
IDENTITY_PATHS = 20
IDENTITY_SLICE_STARTS = 12                 # the first starts at each horizon checked against D-508's rows
P14_PATHS = "a3_brk30_cb20_gate_paths.csv"
SLICES_REFERENCE, SLICES_CONFIG = "customer_slices.csv", "p13_noclose_b20"
#: (arm, firms, mode) -- the reference first
ARMS = (("p14_one_firm", 1, hh.UNHEDGED), ("a_unhedged", 2, hh.UNHEDGED), ("b_hedged", 2, hh.HEDGED),
        ("c_hedged_combines", 2, hh.HEDGED_COMBINES))
SHIFTS = ("point", "lower_bound")
CHUNK = 25                                 # paths a task
SLICE_CHUNK = 120                          # slices a task
WORKER_GB = 0.6                            # one worker's resident memory, rounded up (the guard's divisor)


# ------------------------------------------------------------------------------------------------ the inputs


def align_opposite(t: pd.DataFrame, f: pd.DataFrame) -> pd.DataFrame:
    """The opposite walk's rows in the cell's order: row i of the result is row i of `t`'s event on the other side
    (the same date, decision slot and entry). Refused unless every event of the cell has exactly one."""
    key = ["date", "decision_slot_minutes", "entry_t"]
    a = t[key].copy()
    a["_side"] = np.where(t["side"].astype(str) == "long", 1, -1)
    a["_i"] = np.arange(len(t))
    b = f.copy()
    b["_side"] = -np.where(f["side"].astype(str) == "long", 1, -1)            # the cell's side of the same event
    m = a.merge(b, on=key + ["_side"], how="left", validate="one_to_one", indicator=True)
    if len(m) != len(t) or (m["_merge"] != "both").any():
        raise SystemExit(f"REFUSED ({DECISION}): {int((m['_merge'] != 'both').sum())} of the cell's events have no "
                         "opposite walk.")
    m = m.sort_values("_i").reset_index(drop=True)
    out = m[[c for c in f.columns]].copy()
    if not (np.where(out["side"].astype(str) == "long", 1, -1) == -np.where(t["side"].astype(str) == "long", 1, -1)).all():
        raise SystemExit(f"REFUSED ({DECISION}): the opposite walk is not on the other side of every event.")
    return out


def inputs(rd: Path) -> dict[str, Any]:
    """P-14's campaign exactly as its registered run built it (`a3_brk30_cb20`: the cell's trades, the bounds the gate
    read, the day capacity, the no-closure table through its pinned hashes, the budget, the strict rule), the
    opposite walk aligned to it, and the engine's arguments (`customer_slices.engine_args`, the gate's call)."""
    import a3_brk30 as B
    import a3_brk30_cb20 as C
    import atlas_a3 as A
    import score_fv3_grid as gf

    L = B.inputs()
    t, days = B.cell_trades(L)
    f, fdays = B.cell_trades(L, "fade")
    if list(fdays) != list(days):
        raise SystemExit(f"REFUSED ({DECISION}): the opposite walk's day set is not the cell's.")
    fa = align_opposite(t, f)
    keys = B.rrs(t)
    if B.rrs(fa) != keys:
        raise SystemExit(f"REFUSED ({DECISION}): the opposite walk carries other R values.")
    _, e_by, lb_by, _, flagged = A.bounds(t, days, keys, L["cfg"])
    tv, fcfg = float(L["tv"]), L["fcfg"]
    cell, n1 = gf.gate_blocks(t, days, tv, keys, require_sides=True, require_exits=True)
    opp, n2 = gf.gate_blocks(fa, days, tv, keys, require_sides=True, require_exits=True)
    if n1 != len(t) or n2 != len(t):
        raise SystemExit(f"REFUSED ({DECISION}): the blocks hold a different number of trades.")
    nc = C.noclose_plan(rd)
    cap = B.capacity(t, fcfg)
    horizon = int(fcfg["gate"]["campaign"]["horizon_days"])
    kw = A.gate_kwargs(cell, fcfg, tv, nc, e_by, lb_by, None, seed=SEED, n_paths=N_PATHS, horizon=horizon,
                       capacity=cap, levels=(0.0,), rtp=False, one_at_a_time=C.STRICT_GAP, purchase_budget=C.BUDGET)
    kw.pop("blocks")
    delta = {float(k): float(lb_by[k]) - float(e_by[k]) for k in e_by}
    side = {"long_share": float((t["side"].astype(str) == "long").mean()),
            **{f"e_{R:g}": float(e_by[R]) for R in keys}, **{f"lb_{R:g}": float(lb_by[R]) for R in keys},
            **{f"e_opposite_{R:g}": float(np.nanmean(fa[f"r_{R:g}"].to_numpy(float))) for R in keys}}
    return {"cell": cell, "opposite": opp, "days": days, "kw": kw, "cap": int(cap), "horizon": horizon,
            "delta_r": float(kw["lb"]) - float(kw["e"]), "delta_by_rr": delta, "flagged": bool(flagged),
            "trades": int(len(t)), "policy_id": nc.id, "side": side, "budget": tuple(C.BUDGET),
            "strict_gap": float(C.STRICT_GAP), "margin": float(fcfg["portfolio"]["margin"])}


def arm_blocks(I: dict, shift: str) -> list:
    """The doubled blocks at a shift: as traded, or the cell at its bound and the opposite walk mirrored."""
    if shift == "point":
        return hh.doubled_blocks(I["cell"], I["opposite"])
    if shift != "lower_bound":
        raise ValueError(shift)
    c, o = hh.mirror_shift(I["cell"], I["opposite"], I["delta_r"], I["delta_by_rr"])
    return hh.doubled_blocks(c, o)


def setups(I: dict) -> tuple[hh.FirmSetup, hh.FirmSetup]:
    """(the resampled campaign's setup, the replay's): `customer_slices.engine_args` -- the gate's engine call -- with
    the campaign's funded horizon and Combine limit for the resampled paths, the replay's for the slices; the day
    capacity doubled for the doubled blocks."""
    import customer_slices as cs

    args = cs.engine_args(I["kw"], "point", I["cell"], purchase_budget=I["budget"])
    camp = hh.setup_from_engine_args(args, funded_horizon_days=504, combine_max_days=2000)
    rep = hh.setup_from_engine_args(args)
    return hh.with_capacity(camp, 2 * I["cap"]), hh.with_capacity(rep, 2 * I["cap"])


# ------------------------------------------------------------------------------------------------ the jobs


def _paths_task(task: tuple) -> list[dict]:
    """A worker's share of an arm's paths: (arm, firms, mode, shift, blocks, setup, [(index, seed)], margin, keep0)."""
    import warnings

    warnings.filterwarnings("ignore")
    arm, firms, mode, shift, blocks, setup, items, margin, horizon = task
    specs = [hh.PathSpec(seed=int(s), blocks=blocks, horizon_days=int(horizon)) for _, s in items]
    jps = hh.run_joint(specs, setup, n_firms=int(firms), mode=mode, doubled=True)
    out = []
    for (i, s), jp in zip(items, jps):
        r = hh.path_record(jp, margin=margin)
        r.update({"arm": arm, "shift": shift, "path": int(i), "seed": int(s)})
        out.append(r)
    return out


def _slices_task(task: tuple) -> list[dict]:
    """A worker's share of an arm's slices: (arm, firms, mode, blocks, dates, setup, [(start, horizon)], seed, sub)."""
    import warnings

    warnings.filterwarnings("ignore")
    arm, firms, mode, blocks, dates, setup, items, seed, sub = task
    specs = [hh.PathSpec(seed=int(seed), blocks=blocks[s:s + h], horizon_days=int(h) + 1, replay=True) for s, h in items]
    jps = hh.run_joint(specs, setup, n_firms=int(firms), mode=mode, doubled=True)
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


# ------------------------------------------------------------------------------------------------ the identities


def path_identity(rd: Path, recs: list[dict], n: int) -> list[str]:
    """The reference's first `n` paths (firm 0 alone) against P-14's per-path record, its `gate` run at 0 %, point and
    bound, every `zero_edge_decomposition.PATH_COLS` column (`path_problems`)."""
    import zero_edge_decomposition as zd

    from propedge.reporting.results import read_result

    ref = read_result(rd / P14_PATHS)
    sink = [{"run": "mine", "shift": r["shift"], "enforcement_p": 0.0, "path": r["path"], **r["firm0"]} for r in recs]
    return zd.path_problems(sink, ref, [("mine", s, "gate", s) for s in SHIFTS], int(n))


def slice_identity(rd: Path, sl: pd.DataFrame) -> list[str]:
    """The reference's slices against D-508's `p13_noclose_b20` verdict rows, start for start (`a3_brk30_cb20`'s
    comparison: numbers to 1e-9, flags as flags, dates as text)."""
    import a3_brk30_cb20 as C

    from propedge.reporting.results import read_result

    ref = read_result(rd / SLICES_REFERENCE)
    ref = ref[(ref["section"] == "slice") & (ref["arm"].astype(str) == "verdict")
              & (ref["config"].astype(str) == SLICES_CONFIG)]
    out = []
    for h in sorted({int(x) for x in sl["horizon"]}):
        a = sl[sl["horizon"].astype(int) == h].sort_values("start_day").reset_index(drop=True)
        b = ref[ref["horizon"].astype(int) == h].copy()
        b = b[b["start_day"].astype(int).isin(set(a["start_day"].astype(int)))]
        b = b.sort_values("start_day").reset_index(drop=True)
        if len(a) != len(b) or not (a["start_day"].astype(int).to_numpy() == b["start_day"].astype(int).to_numpy()).all():
            out.append(f"horizon {h}: {len(a)} slices against {len(b)} of {SLICES_CONFIG}")
            continue
        for c in C.SLICE_ID_COLS:
            bad = [i for i in range(len(a)) if not C._slice_same(a[c].iloc[i], b[c].iloc[i])]
            if bad:
                i = bad[0]
                out.append(f"horizon {h} start {int(a['start_day'].iloc[i])} {c}: {a[c].iloc[i]!r} against "
                           f"{b[c].iloc[i]!r} ({len(bad)} differ)")
    return out


# ------------------------------------------------------------------------------------------------ the study


def main(argv: list[str] | None = None, *, results_dir: Path | None = None) -> int:
    from propedge import RESULTS_DIR
    from propedge.campaign.lockstep import path_seeds

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--identity", action="store_true", help="the identities only; nothing written")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--paths", type=int, default=N_PATHS, help="paths an arm (500 for the study)")
    ap.add_argument("--slice-starts", type=int, default=None, help="test seam: only the first starts")
    a = ap.parse_args(argv)
    rd = Path(results_dir) if results_dir is not None else RESULTS_DIR
    t_all = time.time()
    print("P-14's campaign and the opposite walk...", flush=True)
    I = inputs(RESULTS_DIR)
    camp, rep = setups(I)
    margin = I["margin"]                   # one subscription (FV3-C's `portfolio.margin`), the gate's required bankroll
    sub = float(rep.path["subscription"])
    blocks = {s: arm_blocks(I, s) for s in SHIFTS}
    dates = [str(d) for d in I["days"]]
    seeds = path_seeds(SEED, int(a.paths))
    print(f"  {I['trades']} trades on {len(dates)} sessions; capacity {I['cap']} (doubled {2 * I['cap']}); "
          f"{time.time() - t_all:.0f} s", flush=True)

    # 1. the identities, before anything else runs
    print(f"identity: the reference's first {IDENTITY_PATHS} paths against {P14_PATHS}...", flush=True)
    id_tasks = [("p14_one_firm", 1, hh.UNHEDGED, s, blocks[s], camp, list(enumerate(path_seeds(SEED, IDENTITY_PATHS))), margin,
                 I["horizon"]) for s in SHIFTS]
    recs = [r for chunk in _run(id_tasks, _paths_task, a.workers) for r in chunk]
    bad = path_identity(RESULTS_DIR, recs, IDENTITY_PATHS)
    if bad:
        print(f"REFUSED ({DECISION}): one firm's five seats do not reproduce P-14 -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: one firm = the first {IDENTITY_PATHS} paths of {P14_PATHS} (gate, point and bound, 0 %)",
          flush=True)
    vb = blocks["lower_bound"]
    items = [(s, h) for h in HORIZONS for s in range(min(IDENTITY_SLICE_STARTS, len(vb))) if s + h <= len(vb)]
    sl_id = pd.DataFrame(_slices_task(("p14_one_firm", 1, hh.UNHEDGED, vb, dates, rep, items, SLICE_SEED, sub)))
    bad = slice_identity(RESULTS_DIR, sl_id)
    if bad:
        print(f"REFUSED ({DECISION}): one firm's slices are not D-508's {SLICES_CONFIG} -- " + "; ".join(bad[:8]))
        return 3
    print(f"identity HOLDS: one firm's first {IDENTITY_SLICE_STARTS} slices at each horizon = {SLICES_REFERENCE}'s "
          f"{SLICES_CONFIG}", flush=True)
    if a.identity:
        print(f"the identities hold; nothing written (--identity). {time.time() - t_all:.0f} s")
        return 0

    # 2. the arms
    tasks = []
    for arm, firms, mode in ARMS:
        for s in SHIFTS:
            for j in range(0, len(seeds), CHUNK):
                tasks.append((arm, firms, mode, s, blocks[s], camp, list(enumerate(seeds))[j:j + CHUNK], margin,
                              I["horizon"]))
    print(f"the arms: {len(ARMS)} x {len(SHIFTS)} x {len(seeds)} paths...", flush=True)
    paths = [r for chunk in _run(tasks, _paths_task, a.workers) for r in chunk]
    ref_first = [r for r in paths if r["arm"] == "p14_one_firm" and r["path"] < IDENTITY_PATHS]
    bad = path_identity(RESULTS_DIR, ref_first, min(IDENTITY_PATHS, len(seeds)))
    if bad:
        print(f"REFUSED ({DECISION}): the study's reference arm is not P-14's -- " + "; ".join(bad[:8]))
        return 3

    # 3. the slices (the bound-shifted arm, as D-508's verdict rows)
    n_days = len(vb)
    starts = n_days if a.slice_starts is None else int(a.slice_starts)
    items = [(s, h) for h in HORIZONS for s in range(min(starts, n_days)) if s + h <= n_days]
    s_tasks = [(arm, firms, mode, vb, dates, rep, items[j:j + SLICE_CHUNK], SLICE_SEED, sub)
               for arm, firms, mode in ARMS for j in range(0, len(items), SLICE_CHUNK)]
    print(f"the slices: {len(ARMS)} arms x {len(items)} slices...", flush=True)
    sl = pd.DataFrame([r for chunk in _run(s_tasks, _slices_task, a.workers) for r in chunk])
    bad = slice_identity(RESULTS_DIR, sl[sl["config"] == "p14_one_firm"])
    if bad:
        print(f"REFUSED ({DECISION}): the study's reference slices are not D-508's -- " + "; ".join(bad[:8]))
        return 3
    import customer_slices as cs

    summ = cs.summarise(sl)

    # 4. the rows
    return write(rd, results_dir, I, paths, sl, summ, margin, len(seeds), time.time() - t_all, starts=starts)


def write(rd: Path, results_dir: Path | None, I: dict, paths: list[dict], sl: pd.DataFrame, summ: pd.DataFrame,
          margin: float, n_paths: int, seconds: float, *, starts: int) -> int:
    from propedge.backtest.harness import VariantCounter
    from propedge.reporting.results import write_result

    arm_desc = {"p14_one_firm": "reference: one firm's five seats (P-14's configuration, the identity)",
                "a_unhedged": "two firms, ten seats, each signal to one account (never opposite across firms)",
                "b_hedged": "two firms, each signal's lead leg and the other firm's account in its slot on the "
                            "opposite side (paired by slot, D-203)",
                "c_hedged_combines": "as b_hedged only when both legs are Combines; funded accounts unhedged"}
    rows: list[dict] = [
        {"section": "identity", "check": f"one firm's five seats (the reference arm) reproduce the first "
                                         f"{IDENTITY_PATHS} paths of {P14_PATHS}'s gate run at seed {SEED}, point "
                                         "and bound, 0 % (zero_edge_decomposition.PATH_COLS)", "holds": True},
        {"section": "identity", "check": f"the reference arm's slices equal {SLICES_REFERENCE}'s {SLICES_CONFIG} "
                                         "verdict rows, start for start at 21, 63 and 126 sessions", "holds": True}]
    for arm, firms, mode in ARMS:
        for s in SHIFTS:
            recs = [r for r in paths if r["arm"] == arm and r["shift"] == s]
            rows.append({"section": "arm", "arm": arm, "firms": firms, "mode": mode, "shift": s,
                         "arm_text": arm_desc[arm], **hh.readings(recs, margin=margin)})
    summ = summ.copy()
    summ["section"] = "slices"
    summ = summ.rename(columns={"config": "arm_slices"})
    summ["arm"] = summ["arm_slices"]
    summ = summ.drop(columns=["arm_slices"])
    summ["shift"] = "lower_bound"
    res = pd.concat([pd.DataFrame(rows), summ], ignore_index=True)
    res.insert(0, "label", hh.TAG)
    hh.require_label(res.to_dict("records"))
    per_path = pd.DataFrame([{"label": hh.TAG, "arm": r["arm"], "shift": r["shift"], "path": r["path"],
                              "seed": r["seed"], "initial": r["initial"], "net": r["net"], "fees": r["fees"],
                              "payouts_dollars": r["payouts_dollars"], "deepest_loss_from_start":
                              r["deepest_loss_from_start"], "needed": r["needed"],
                              "combines_started": r["combines_started"], "combines_resolved": len(r["resolved"]),
                              "passes": len(r["pass_days"]), "payouts": len(r["pay_days"]),
                              "pass_days": " ".join(str(d) for d in r["pass_days"]),
                              "pay_days": " ".join(str(d) for d in r["pay_days"]),
                              "resolved_passed": "".join("1" if ok else "0" for _, ok in r["resolved"]),
                              "pairs": r["pairs"], "pairs_with_pass": r["pairs_with_pass"],
                              "pairs_both_pass": r["pairs_both_pass"], "pair_passes": r["pair_passes"],
                              **{f"deal_{k}": (v if not isinstance(v, list) else " ".join(str(x) for x in v))
                                 for k, v in r["deal"].items()}} for r in paths])
    hh.require_label(per_path.to_dict("records"))
    counter = VariantCounter(path=Path(rd) / "variants.jsonl")
    for arm, firms, mode in ARMS[1:]:
        counter.record(prereg_id=hh.VARIANT, seed=SEED, exploratory=True,
                       params={"study": "the cross-firm hedge pair on P-14's design", "decision": DECISION,
                               "arm": arm, "mode": mode, "firms": firms, "paths": n_paths},
                       label=f"{hh.TAG}: {arm} ({DECISION}) -- {hh.LABEL}")
    params = {"decision": DECISION, "label": hh.TAG, "status": hh.LABEL, "seed": SEED, "slice_seed": SLICE_SEED,
              "n_paths": n_paths, "horizon": I["horizon"], "horizons": list(HORIZONS), "slice_starts": starts,
              "arms": [{"arm": a, "firms": f, "mode": m, "text": arm_desc[a]} for a, f, m in ARMS],
              "firms": "two firms with Topstep's verified contract (Firm H's convention, D-203; rules_for_method"
                       "('aeropay') from the verified ledger), five seats each, one pooled wallet (D-206)",
              "protocol": "P-14's (a3_brk30_cb20): atlas_a3.gate_kwargs -- FV3-C's engine call, the day capacity at "
                          "the cell's busiest day (doubled for the doubled blocks), the strict rule PER FIRM, the "
                          "no-closure table, the purchase budget per firm -- through customer_slices.engine_args",
              "policy_id": I["policy_id"], "budget": list(I["budget"]), "strict_gap_minutes": I["strict_gap"],
              "capacity": I["cap"], "capacity_doubled": 2 * I["cap"], "trades": I["trades"],
              "sessions": len(I["days"]), "first": str(I["days"][0]), "last": str(I["days"][-1]),
              "bound": {"delta_r": I["delta_r"], "delta_by_rr": {f"{k:g}": v for k, v in I["delta_by_rr"].items()},
                        "rule": "the cell's trades at the 0.05 bound of e at each R (the gate row's shift, era rule "
                                f"flagged={I['flagged']}); the opposite walk moved the same amount the other way"},
              "sides": I["side"],
              "deal": "propedge.research.hypo_hedge.HedgeRouter: one position per firm (5-minute gap); the lead leg "
                      "as two_firms.JointRouter (never opposite to a position open at the other firm, the firm waiting "
                      "longest, its longest-waiting account able to take it); the partner leg in the lead's slot at "
                      "the other firm on the opposite side (hedged arms), counted unhedged when it cannot",
              "conduct": "ConductModel(rtp=False, enforcement_p=0.0): placement off, 0 % denial -- no consequence; "
                         "the hypothetical firm allows the pattern",
              "bankroll": "the gate's unbound bankroll, one pool per path; required bankroll = deepest pooled loss "
                          f"from the start + {margin:g} (portfolio.measures), growth on it at p90",
              "slices": "customer_slices' replay and summary (D-508), the bound-shifted arm, pooled cash, every "
                        "firm's passes and payouts",
              "identity": {"paths": IDENTITY_PATHS, "paths_file": P14_PATHS, "slices_file": SLICES_REFERENCE,
                           "slices_config": SLICES_CONFIG},
              "seconds": round(float(seconds), 1),
              "bars": "data/bars/NQ (Databento GLBX.MDP3 ohlcv-1m, D-458)"}
    write_result(res, RESULT, script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir, parameters=params,
                 notes={"decisions": ["D-153", "D-203", "D-206", "D-452", "D-514"], "status": hh.LABEL,
                        "label": hh.TAG},
                 description="HYPOTHETICAL (hypothetical_hedge, D-514): the cross-firm hedge pair on P-14's design -- "
                             "two Topstep-contract firms of five seats on one pooled wallet, unhedged, hedged by slot, "
                             "and hedged on the Combines only, beside one firm's five seats (P-14, the identity); "
                             "growth on the required bankroll, pass and payout consistency, cost per pass, and the "
                             "customer slices. Prohibited conduct (tier 1); never a candidate.")
    write_result(per_path, f"{RESULT}_paths", script=SCRIPT, seed=SEED, exploratory=True, results_dir=results_dir,
                 parameters={"result": f"{RESULT}.csv", "label": hh.TAG},
                 notes={"status": hh.LABEL, "companion_of": f"{RESULT}.csv", "label": hh.TAG},
                 description=f"HYPOTHETICAL (hypothetical_hedge): the per-path record of {RESULT}.csv.")
    pd.set_option("display.width", 250)
    show = ["arm", "shift", "growth_on_required", "required_p90", "pass_rate_per_combine", "passes_mean",
            "share_paths_no_pass_first_21", "chance_no_pass_in_5_combines", "days_between_passes_p50",
            "days_between_payouts_p50", "cost_per_pass", "payouts_per_month_mean", "share_dealt_signals_hedged"]
    print(hh.LABEL)
    print(pd.DataFrame(rows[2:])[show].round(4).to_string(index=False))
    print(summ[["arm", "horizon", "share_positive", "net_p10", "share_no_payout", "needed_bankroll_p95"]]
          .round(3).to_string(index=False))
    print(f"written: {RESULT}.csv and {RESULT}_paths.csv ({seconds:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
