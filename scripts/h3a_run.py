"""H3-A: the three-way test's design checks (`prereg/H3_three_way.md` sections 8, 10, 11, 15-17; E-279, E-285).

Runs one declared H3-A slot at a time from a clean checkout under `run.lock` (`OMP_NUM_THREADS=1`, at most 2 workers):

    python scripts/run_clean.py --name h3a-a1   --hours 7.5 --mem-gb 1.0 --task Q-187 -- python scripts/h3a_run.py --part A1   --workers 2
    python scripts/run_clean.py --name h3a-a2   --hours 5.5 --mem-gb 1.0 --task Q-187 -- python scripts/h3a_run.py --part A2   --workers 2
    python scripts/run_clean.py --name h3a-a3-1 --hours 5.5 --mem-gb 1.0 --task Q-187 -- python scripts/h3a_run.py --part A3_1 --workers 2
    python scripts/run_clean.py --name h3a-a3-2 --hours 5.5 --mem-gb 1.0 --task Q-187 -- python scripts/h3a_run.py --part A3_2 --workers 2
    python scripts/run_clean.py --name h3a-a4-1 --hours 5.5 --mem-gb 1.0 --task Q-187 -- python scripts/h3a_run.py --part A4_1 --workers 2
    python scripts/run_clean.py --name h3a-a4-2 --hours 5.5 --mem-gb 1.0 --task Q-187 -- python scripts/h3a_run.py --part A4_2 --workers 2
    python scripts/run_clean.py --name h3a-rep  --commit <sha>                         -- python scripts/h3a_run.py --part report

Refuses BEFORE any draw unless:
- `extended.h3a_report.assert_h3_preconditions(ROOT, check_build_commit=True)` holds (H3 pinned at E-279, Template v3
  pinned at E-284 with matching R-10 clauses, all 9 build files unchanged since `4c07026`);
- clean checkout (`S2X_CLEAN_RUN`), `run.lock` held by this job (for compute parts), and output CSV/manifest absent.

Zero raw H3 seed literals appear in this script or its result manifests; every seed is issued by role through
`extended.three_way_seeds.issue(...)`.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import math
import os
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import RESULTS_DIR  # noqa: E402
from extended import family_stats as FS  # noqa: E402
from extended import h3a_report as REP  # noqa: E402
from extended import lock_guard as LG  # noqa: E402
from extended import three_way_h3a as H  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_runner as R  # noqa: E402
from extended import three_way_s1 as S1  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402
from extended import three_way_stats as ST  # noqa: E402

SCRIPT = "scripts/h3a_run.py"
MAX_WORKERS = 2

#: E-285 declared H3-A slot splits (histories range, seed count M)
SLOT_SPEC: dict[str, dict[str, Any]] = {
    "A1": {"part": "A1", "histories": (0, 20), "M": H.SEEDS, "out": "h3a_a1"},
    "A2": {"part": "A2", "histories": (0, 20), "M": H.SEEDS, "out": "h3a_a2"},
    "A3_1": {"part": "A3", "histories": (0, 100), "M": 2000, "out": "h3a_a3_1"},
    "A3_2": {"part": "A3", "histories": (100, 200), "M": 2000, "out": "h3a_a3_2"},
    "A4_1": {"part": "A4", "histories": (0, 5), "M": H.SEEDS, "out": "h3a_a4_1"},
    "A4_2": {"part": "A4", "histories": (5, 10), "M": H.SEEDS, "out": "h3a_a4_2"},
    "report": {"part": "report", "out": "h3a_summary"},
}


# ----------------------------------------------------------------------------------------- composite & dimension helpers


def dim_matrices(recs: Sequence[J.Records], *, horizon: int = H.HORIZON) -> dict[str, np.ndarray]:
    """Extract all three `TOY_COMPOSITE` per-unit matrices (`P_B`, `paid_by_63`, `sessions_saved_to_payout`) from one
    `Records` list (shape `(len(starts), len(seed_indices))`)."""
    pb = R.matrix(recs, R.p_b)
    paid = R.matrix(recs, lambda rec: ((rec.first_pay > 0) & (rec.first_pay <= horizon)).astype(float))
    saved = R.matrix(recs, lambda rec: float(horizon + 1) - J.days_to_first_payout(rec, horizon))
    return {"P_B": pb, "paid_by_63": paid, "sessions_saved_to_payout": saved}


def exact_dim_expectations(
    schedule: J.Schedule,
    rules: J.ToyRules,
    starts: Sequence[int],
    horizon: int,
    *,
    block_sessions: int,
    budget: float | None,
    arm: J.ArmSpec = J.ArmSpec(),
) -> dict[str, np.ndarray]:
    """Exact per-start expectations for all three `TOY_COMPOSITE` dimensions via `three_way_journey`'s exact DP."""
    n = len(starts)
    out = {"P_B": np.zeros(n, float), "paid_by_63": np.zeros(n, float), "sessions_saved_to_payout": np.zeros(n, float)}
    for idx, s in enumerate(starts):
        J.check_window(s, horizon, block_sessions)
        J.check_costs(schedule, rules, arm)
        L = J.fresh(1, rules)
        for k in range(1, horizon + 1):
            L = J._session(L, schedule.by_session.get(s + k - 1, ()), k, rules, arm, budget, None, dp=True)
            L.day = L.dead = L.stopped = None
            L = J._merge(L, rules, budget)
        w = np.asarray(L.w, float)
        tot = float(w.sum())
        if abs(tot - 1.0) > 1e-6:
            raise REP.H3ReportRefused(f"exact DP total probability {tot} != 1.0 at start {s}")
        fp = np.asarray(L.first_pay, float)
        paid = ((fp > 0) & (fp <= horizon)).astype(float)
        days = np.where((fp > 0) & (fp <= horizon), fp, float(horizon + 1))
        saved = float(horizon + 1) - days
        out["P_B"][idx] = float((w * L.ahead).sum() / 3.0)
        out["paid_by_63"][idx] = float((w * paid).sum())
        out["sessions_saved_to_payout"][idx] = float((w * saved).sum())
    return out


def composite_per_seed_diffs(
    Xf: Mapping[str, np.ndarray],
    Xb: Mapping[str, np.ndarray],
    dims: Sequence[ST.Dimension],
) -> np.ndarray:
    """One composite difference Delta_j in [-1, 1] per seed column (mean over starts, clipped and weighted)."""
    n_seeds = next(iter(Xf.values())).shape[1]
    out = np.zeros(n_seeds, float)
    for d in dims:
        vf = d.values(Xf[d.name]).mean(axis=0)
        vb = d.values(Xb[d.name]).mean(axis=0)
        sf = np.clip((vf - d.lo) / (d.hi - d.lo), 0.0, 1.0)
        sb = np.clip((vb - d.lo) / (d.hi - d.lo), 0.0, 1.0)
        out += d.weight * (sf - sb)
    return out


def eval_size_sets(
    Xf: Mapping[str, np.ndarray],
    Xb: Mapping[str, np.ndarray],
    starts: Sequence[int],
    *,
    j_prime: int,
    levels: Sequence[float] = REP.LEVELS,
) -> dict[tuple[str, str, float], tuple[int, int]]:
    """Evaluate rejection counts `(rejections, n_sets)` across disjoint seed sets of size `j_prime` for both
    composites (`p_b`, `toy_composite`), all three bounds (`bound_22a`, `eb`, `betting`), and all `levels`."""
    n_seeds = Xf["P_B"].shape[1]
    sets = R.seed_sets(n_seeds, j_prime)
    if not sets:
        raise REP.H3ReportRefused(f"no seed sets of size {j_prime} from {n_seeds} seeds")
    pb_dims = (ST.fallback(),)
    toy_dims = H.TOY_COMPOSITE
    starts_map_pb = {"P_B": starts}
    starts_map_toy = {d.name: starts for d in toy_dims}

    counts: dict[tuple[str, str, float], int] = {
        (comp, b, float(lvl)): 0
        for comp in REP.COMPOSITES
        for b in REP.BOUNDS
        for lvl in levels
    }

    for cols in sets:
        xf_s = {k: v[:, cols] for k, v in Xf.items()}
        xb_s = {k: v[:, cols] for k, v in Xb.items()}
        d_pb = composite_per_seed_diffs(xf_s, xb_s, pb_dims)
        d_toy = composite_per_seed_diffs(xf_s, xb_s, toy_dims)
        for lvl in levels:
            lv = float(lvl)
            if ST.mcdiarmid(pb_dims, {"P_B": xf_s["P_B"]}, {"P_B": xb_s["P_B"]}, starts_map_pb, lv).rejects:
                counts[("p_b", "bound_22a", lv)] += 1
            if ST.eb_lower(d_pb, lv) > 0.0:
                counts[("p_b", "eb", lv)] += 1
            if ST.betting_lower(d_pb, lv) > 0.0:
                counts[("p_b", "betting", lv)] += 1

            if ST.mcdiarmid(toy_dims, xf_s, xb_s, starts_map_toy, lv).rejects:
                counts[("toy_composite", "bound_22a", lv)] += 1
            if ST.eb_lower(d_toy, lv) > 0.0:
                counts[("toy_composite", "eb", lv)] += 1
            if ST.betting_lower(d_toy, lv) > 0.0:
                counts[("toy_composite", "betting", lv)] += 1

    n_sets = len(sets)
    return {k: (v, n_sets) for k, v in counts.items()}


# ----------------------------------------------------------------------------------------- runtime & precondition gates


def check_runtime_gates(
    part: str,
    *,
    root: Path = ROOT,
    results_dir: Path = RESULTS_DIR,
    require_lock: bool = True,
) -> dict[str, str]:
    """Section 16 item 1: H3 pin + template v3 + `4c07026` build files + clean run + run.lock + output absent."""
    from extended import results as RES

    pre = REP.assert_h3_preconditions(root, check_build_commit=True)
    bad_clean = RES.clean_run_problem()
    if bad_clean:
        raise REP.H3ReportRefused(f"H3-A requires a clean run (scripts/run_clean.py): {bad_clean}")
    if require_lock:
        holder = os.environ.get(LG.LOCK_HOLDER_ENV, "").strip()
        if not holder:
            raise REP.H3ReportRefused(f"H3-A {part} requires run.lock ({LG.LOCK_HOLDER_ENV} unset)")
        mroot = LG.main_root(root)
        if mroot is None:
            raise REP.H3ReportRefused(f"cannot resolve main root for run.lock from {root}")
        lock_file = mroot / LG.LOCK_NAME
        if not lock_file.is_file():
            raise REP.H3ReportRefused(f"run.lock not found at {lock_file}")
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
        if not isinstance(lock_data, dict) or lock_data.get("job") != holder:
            raise REP.H3ReportRefused(f"run.lock job != {LG.LOCK_HOLDER_ENV} ({holder!r})")
    out_csv = Path(results_dir) / f"{SLOT_SPEC[part]['out']}.csv"
    out_man = RES.manifest_path_for(out_csv)
    if out_csv.exists() or out_man.exists():
        raise REP.H3ReportRefused(f"output already exists: {out_csv} (refusing to overwrite)")
    return pre


# ----------------------------------------------------------------------------------------- per-history workers


def _a1_one_history(args: tuple[int, int, tuple[int, ...], int, int, int, S1.S1Params, J.ToyRules]) -> dict[str, Any]:
    r, M, starts, horizon, j_prime, part_id, s1_params, rules = args
    h_seed = S.issue("h3a_histories")
    c_seed = S.issue("h3a_coins")
    hist = S1.generate(h_seed, part_id, r, s1_params)
    sched = S1.schedule(H.A1_DESIGN, hist)

    plan_full = R.Plan(
        seed=c_seed, part=part_id, history=r, starts=starts, seed_indices=range(M),
        horizon=horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET,
    )
    g_base = K.KeyGuard.sampled(plan_full.starts, plan_full.seed_indices)
    recs_base = R.run(sched, rules, plan_full, J.ArmSpec(), g_base)
    recs_twin = R.run(sched, rules, plan_full, J.ArmSpec(twin=True), g_base)

    X_base = dim_matrices(recs_base, horizon=horizon)
    X_twin = dim_matrices(recs_twin, horizon=horizon)

    # Disjoint split: first half vs second half of the M seeds (identical to H.DISJOINT at M=10_000)
    half = M // 2
    g1 = K.KeyGuard.sampled(plan_full.starts, range(0, half))
    g2 = K.KeyGuard.sampled(plan_full.starts, range(half, M))
    # Verify disjoint key states on first start
    X_d1 = {k: v[:, :half] for k, v in X_base.items()}
    X_d2 = {k: v[:, half:M] for k, v in X_base.items()}
    # Key-state disjointness check via sample keys on start 0
    for s_idx in plan_full.starts[:1]:
        for c_i in range(min(K.SAMPLE_SEEDS, half)):
            g1.add(K.seed_key(c_seed, "coin", part=part_id, history=r, seed_index=c_i, start=s_idx, underlying=0,
                              moment=0, draw_kind=K.RACE), start=s_idx, seed_index=c_i)
            g2.add(K.seed_key(c_seed, "coin", part=part_id, history=r, seed_index=half + c_i, start=s_idx,
                              underlying=0, moment=0, draw_kind=K.RACE), start=s_idx, seed_index=half + c_i)
    K.disjoint(g1, g2)

    anti_pb = composite_per_seed_diffs(X_base, X_twin, (ST.fallback(),))
    anti_toy = composite_per_seed_diffs(X_base, X_twin, H.TOY_COMPOSITE)
    disj_pb = composite_per_seed_diffs(X_d1, X_d2, (ST.fallback(),))
    disj_toy = composite_per_seed_diffs(X_d1, X_d2, H.TOY_COMPOSITE)

    # Premise checks (section 11): centring & non-degenerate variance
    single_var_pb = float(X_d1["P_B"].mean(axis=0).var(ddof=1))
    single_var_toy = float(
        sum(
            d.weight * np.clip((d.values(X_d1[d.name]).mean(axis=0) - d.lo) / (d.hi - d.lo), 0.0, 1.0)
            for d in H.TOY_COMPOSITE
        ).var(ddof=1)
    )
    prem = {
        "anti_pb": REP.check_null_pool(anti_pb),
        "anti_toy": REP.check_null_pool(anti_toy),
        "disj_pb": REP.check_null_pool(disj_pb, single_arm_var=single_var_pb),
        "disj_toy": REP.check_null_pool(disj_toy, single_arm_var=single_var_toy),
    }

    anti_counts = eval_size_sets(X_base, X_twin, starts, j_prime=j_prime)
    disj_counts = eval_size_sets(X_d1, X_d2, starts, j_prime=j_prime)

    return {
        "history": r,
        "anti_counts": anti_counts,
        "disj_counts": disj_counts,
        "anti_pb_sd": float(anti_pb.std(ddof=1)),
        "anti_toy_sd": float(anti_toy.std(ddof=1)),
        "premise": prem,
        "fill_failures": R.fill_failures(recs_base),
    }


def _a2_one_history(args: tuple[int, int, tuple[int, ...], int, int, int, S1.S1Params, J.ToyRules]) -> dict[str, Any]:
    r, M, starts, horizon, j_prime, part_id, s1_params, rules = args
    h_seed = S.issue("h3a_histories")
    c_seed = S.issue("h3a_coins")
    hist = S1.generate(h_seed, part_id, r, s1_params)
    f_sch = S1.schedule(H.A2_PAIR[0], hist)
    b_sch = S1.schedule(H.A2_PAIR[1], hist)

    plan = R.Plan(
        seed=c_seed, part=part_id, history=r, starts=starts, seed_indices=range(M),
        horizon=horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET,
    )
    guard = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    recs_f = R.run(f_sch, rules, plan, J.ArmSpec(), guard)
    recs_b = R.run(b_sch, rules, plan, J.ArmSpec(), guard)

    Xf = dim_matrices(recs_f, horizon=horizon)
    Xb = dim_matrices(recs_b, horizon=horizon)

    ef = exact_dim_expectations(f_sch, rules, starts, horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET)
    eb = exact_dim_expectations(b_sch, rules, starts, horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET)

    # Centre Xf against Xb by subtracting each dimension's exact per-start difference theta_d = E[f] - E[b]
    Xf_c: dict[str, np.ndarray] = {}
    Xb_c: dict[str, np.ndarray] = {}
    for d in H.TOY_COMPOSITE:
        theta = (ef[d.name] - eb[d.name])[:, None]
        # Shift symmetrically within arithmetic bounds by centring the difference D = Xf - Xb - theta
        # For McDiarmid/EB/Betting on centred differences: compare (Xf - theta_pos) vs (Xb + theta_neg) clipped to [a, a+r]
        # Exact shift: evaluate on centred per-unit values directly
        Xf_c[d.name] = np.clip(Xf[d.name] - np.maximum(theta, 0.0), d.a, d.a + d.r)
        Xb_c[d.name] = np.clip(Xb[d.name] + np.minimum(theta, 0.0), d.a, d.a + d.r)

    # Exact raw centred per-seed differences (unclipped shift for premise centring check)
    raw_d_pb = (Xf["P_B"] - Xb["P_B"] - (ef["P_B"] - eb["P_B"])[:, None]).mean(axis=0)
    prem_pb = REP.check_null_pool(raw_d_pb)

    counts = eval_size_sets(Xf_c, Xb_c, starts, j_prime=j_prime)
    return {
        "history": r,
        "counts": counts,
        "premise_pb": prem_pb,
        "theta_pb_mean": float((ef["P_B"] - eb["P_B"]).mean()),
    }


def _a3_one_history(args: tuple[int, int, tuple[int, ...], int, int, S1.S1Params, J.ToyRules]) -> dict[str, Any]:
    r, M, starts, horizon, part_id, s1_params, rules = args
    # Section 15: A3 draws histories, stream swaps, AND coin fields from h3a3_history_null ONLY
    a3_seed = S.issue("h3a3_history_null")
    hist = S1.generate(a3_seed, part_id, r, s1_params)
    f_sch = S1.schedule(H.A3_PAIR[0], hist)
    b_sch = S1.schedule(H.A3_PAIR[1], hist)
    plan = R.Plan(
        seed=a3_seed, part=part_id, history=r, starts=starts, seed_indices=range(M),
        horizon=horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET,
    )
    guard = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    xf = R.matrix(R.run(f_sch, rules, plan, J.ArmSpec(), guard), R.p_b)
    xb = R.matrix(R.run(b_sch, rules, plan, J.ArmSpec(), guard), R.p_b)
    d = (xf - xb).mean(axis=0)
    row: dict[str, Any] = {"history": r, "mean_diff": float(d.mean()), "sd_diff": float(d.std(ddof=1))}
    for lvl in REP.LEVELS:
        lv = float(lvl)
        row[f"rej_bound_22a_{lv:g}"] = int(
            ST.mcdiarmid((ST.fallback(),), {"P_B": xf}, {"P_B": xb}, {"P_B": starts}, lv).rejects
        )
        row[f"rej_eb_{lv:g}"] = int(ST.eb_lower(d, lv) > 0.0)
        row[f"rej_betting_{lv:g}"] = int(ST.betting_lower(d, lv) > 0.0)
    return row


def _a4_one_history(args: tuple[int, int, tuple[int, ...], int, int, S1.S1Params, J.ToyRules]) -> list[dict[str, Any]]:
    r, M, starts, horizon, part_id, s1_params, rules = args
    h_seed = S.issue("h3a_histories")
    c_seed = S.issue("h3a_coins")
    hist = S1.generate(h_seed, part_id, r, s1_params)
    sched = S1.schedule(H.A1_DESIGN, hist)
    plan = R.Plan(
        seed=c_seed, part=part_id, history=r, starts=starts, seed_indices=range(M),
        horizon=horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET,
    )
    guard = K.KeyGuard.sampled(plan.starts, plan.seed_indices)
    x_base = R.matrix(R.run(sched, rules, plan, J.ArmSpec(), guard), R.p_b)
    rows: list[dict[str, Any]] = []

    # P1 linear plants on P_B (section 10)
    for delta in H.SIZE_GRID:
        xf = np.clip(x_base + float(delta), 0.0, 1.0)
        d = (xf - x_base).mean(axis=0)
        for lvl in REP.LEVELS:
            lv = float(lvl)
            rows.append({
                "history": r, "plant": "P1", "param": f"delta={delta:g}", "level": lv,
                "mean_diff": float(d.mean()),
                "rej_bound_22a": int(ST.mcdiarmid((ST.fallback(),), {"P_B": xf}, {"P_B": x_base}, {"P_B": starts}, lv).rejects),
                "rej_eb": int(ST.eb_lower(d, lv) > 0.0),
                "rej_betting": -1,  # P1 refused for betting bound (m-12)
            })

    # P2 lever changes (section 10)
    for name, patch in H.P2_LEVERS.items():
        r2 = replace(rules, **patch)
        xf = R.matrix(R.run(sched, r2, plan, J.ArmSpec(), guard), R.p_b)
        d = (xf - x_base).mean(axis=0)
        for lvl in REP.LEVELS:
            lv = float(lvl)
            rows.append({
                "history": r, "plant": "P2", "param": name, "level": lv,
                "mean_diff": float(d.mean()),
                "rej_bound_22a": int(ST.mcdiarmid((ST.fallback(),), {"P_B": xf}, {"P_B": x_base}, {"P_B": starts}, lv).rejects),
                "rej_eb": int(ST.eb_lower(d, lv) > 0.0),
                "rej_betting": int(ST.betting_lower(d, lv) > 0.0),
            })

    # P3 edge plants (section 10)
    for eps in H.P3_EPS:
        xf = R.matrix(R.run(sched, rules, plan, J.ArmSpec(plant_eps=float(eps)), guard), R.p_b)
        d = (xf - x_base).mean(axis=0)
        for lvl in REP.LEVELS:
            lv = float(lvl)
            rows.append({
                "history": r, "plant": "P3", "param": f"eps={eps:g}", "level": lv,
                "mean_diff": float(d.mean()),
                "rej_bound_22a": int(ST.mcdiarmid((ST.fallback(),), {"P_B": xf}, {"P_B": x_base}, {"P_B": starts}, lv).rejects),
                "rej_eb": int(ST.eb_lower(d, lv) > 0.0),
                "rej_betting": int(ST.betting_lower(d, lv) > 0.0),
            })

    # P4 regime-varying plants (section 10)
    rho = FS.slow_sign(
        np.random.default_rng(K.seed_key(h_seed, "plant", part=part_id, history=r, plant=4, replicate=0)),
        len(starts),
        H.P4_SWITCH,
    )
    for delta in H.SIZE_GRID:
        for a_val in H.P4_A:
            shift = float(delta) * (1.0 + float(a_val) * rho)[:, None]
            xf = np.clip(x_base + shift, 0.0, 1.0)
            d = (xf - x_base).mean(axis=0)
            for lvl in REP.LEVELS:
                lv = float(lvl)
                rows.append({
                    "history": r, "plant": "P4", "param": f"d={delta:g},a={a_val:g}", "level": lv,
                    "mean_diff": float(d.mean()),
                    "rej_bound_22a": int(ST.mcdiarmid((ST.fallback(),), {"P_B": xf}, {"P_B": x_base}, {"P_B": starts}, lv).rejects),
                    "rej_eb": int(ST.eb_lower(d, lv) > 0.0),
                    "rej_betting": int(ST.betting_lower(d, lv) > 0.0),
                })

    return rows


# ----------------------------------------------------------------------------------------- part orchestrators


def _map_workers(fn, tasks: list, workers: int) -> list:
    w = max(1, min(int(workers), MAX_WORKERS))
    if w == 1 or len(tasks) <= 1:
        return [fn(t) for t in tasks]
    with cf.ProcessPoolExecutor(max_workers=w) as ex:
        return list(ex.map(fn, tasks))


def run_a1(
    *,
    histories: Sequence[int] = range(20),
    M: int = H.SEEDS,
    starts: tuple[int, ...] = H.STARTS,
    horizon: int = H.HORIZON,
    j_prime: int = H.J_PRIME,
    s1_params: S1.S1Params = H.S1_PARAMS,
    rules: J.ToyRules = H.TOY_RULES,
    workers: int = 2,
    run_smaller_j: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    part_id = S.PARTS["A1"]
    tasks = [(int(r), int(M), starts, int(horizon), int(j_prime), part_id, s1_params, rules) for r in histories]
    res = _map_workers(_a1_one_history, tasks, workers)

    # Check premises across every history
    premise_fails = [
        (item["history"], k, v["abs_z"])
        for item in res
        for k, v in item["premise"].items()
        if not v["ok"]
    ]
    if premise_fails:
        raise REP.H3ReportRefused(f"A1 centring premise failed (|z| > {H.CENTRING_Z}): {premise_fails[:5]}")

    pooled_acc: dict[tuple[str, str, str, float], list[int]] = {}
    per_hist_rows: list[dict[str, Any]] = []
    for item in res:
        r = item["history"]
        for nc, key in (("antithetic", "anti_counts"), ("disjoint", "disj_counts")):
            for (comp, b, lvl), (rej, n_s) in item[key].items():
                pk = (nc, comp, b, lvl)
                acc = pooled_acc.setdefault(pk, [0, 0])
                acc[0] += rej
                acc[1] += n_s
                per_hist_rows.append(
                    REP.score_per_history_beside(
                        REP.SizeCount("A1", nc, comp, b, lvl, rej, n_s, history=r)
                    )
                )

    pooled_rows = [
        REP.score_pooled_cell(REP.SizeCount("A1", nc, comp, b, lvl, rej, n_s))
        for (nc, comp, b, lvl), (rej, n_s) in sorted(pooled_acc.items())
    ]

    # A1 stress runs (15 runs on history 0: A1_DESIGN + 4 BASELINES x 3 stress arms)
    hist0 = S1.generate(S.issue("h3a_histories"), part_id, int(histories[0]), s1_params)
    plan0 = R.Plan(
        seed=S.issue("h3a_coins"), part=part_id, history=int(histories[0]), starts=starts,
        seed_indices=range(min(int(M), 64)), horizon=horizon, block_sessions=s1_params.n_sessions, budget=H.BUDGET,
    )
    stress_out = R.stress(
        S1.schedule(H.A1_DESIGN, hist0),
        {name: S1.schedule(spec, hist0) for name, spec in H.BASELINES.items()},
        rules,
        plan0,
        R.p_b,
    )
    stress_summary = {
        arm_name: {k: float(v.mean()) for k, v in mats.items()}
        for arm_name, mats in stress_out.items()
    }

    # Smaller-J report (single threaded generator via H.smaller_j_rng)
    smaller_j_info: dict[str, Any] = {}
    if run_smaller_j:
        rng = H.smaller_j_rng()
        sd_pb = float(np.mean([item["anti_pb_sd"] for item in res]))
        sd_toy = float(np.mean([item["anti_toy_sd"] for item in res]))
        smaller_j_info["p_b"] = ST.smaller_j(
            delta=0.01, sigma=sd_pb, alpha=REP.LEVELS[0], power=FS.MDL_POWER, rng=rng
        )
        smaller_j_info["toy_composite"] = ST.smaller_j(
            delta=0.01, sigma=sd_toy, alpha=REP.LEVELS[0], power=FS.MDL_POWER, rng=rng
        )

    meta = {
        "part": "A1",
        "histories": [int(r) for r in histories],
        "M": int(M),
        "j_prime": int(j_prime),
        "seed_roles": ["h3a_histories", "h3a_coins"],
        "stress_arms_count": sum(len(v) for v in stress_summary.values()),
        "stress_summary": stress_summary,
        "smaller_j_report": smaller_j_info,
    }
    return pd.DataFrame(pooled_rows), pd.DataFrame(per_hist_rows), meta


def run_a2(
    *,
    histories: Sequence[int] = range(20),
    M: int = H.SEEDS,
    starts: tuple[int, ...] = H.STARTS,
    horizon: int = H.HORIZON,
    j_prime: int = H.J_PRIME,
    s1_params: S1.S1Params = H.S1_PARAMS_EXACT,
    rules: J.ToyRules = H.TOY_RULES_EXACT,
    workers: int = 2,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    part_id = S.PARTS["A2"]
    tasks = [(int(r), int(M), starts, int(horizon), int(j_prime), part_id, s1_params, rules) for r in histories]
    res = _map_workers(_a2_one_history, tasks, workers)

    premise_fails = [(item["history"], item["premise_pb"]["abs_z"]) for item in res if not item["premise_pb"]["ok"]]
    if premise_fails:
        raise REP.H3ReportRefused(f"A2 exact-centring premise failed: {premise_fails[:5]}")

    pooled_acc: dict[tuple[str, str, float], list[int]] = {}
    per_hist_rows: list[dict[str, Any]] = []
    for item in res:
        r = item["history"]
        for (comp, b, lvl), (rej, n_s) in item["counts"].items():
            acc = pooled_acc.setdefault((comp, b, lvl), [0, 0])
            acc[0] += rej
            acc[1] += n_s
            per_hist_rows.append(
                REP.score_per_history_beside(
                    REP.SizeCount("A2", "exact_centred", comp, b, lvl, rej, n_s, history=r)
                )
            )
    pooled_rows = [
        REP.score_pooled_cell(REP.SizeCount("A2", "exact_centred", comp, b, lvl, rej, n_s))
        for (comp, b, lvl), (rej, n_s) in sorted(pooled_acc.items())
    ]
    meta = {
        "part": "A2",
        "histories": [int(r) for r in histories],
        "M": int(M),
        "j_prime": int(j_prime),
        "seed_roles": ["h3a_histories", "h3a_coins"],
    }
    return pd.DataFrame(pooled_rows), pd.DataFrame(per_hist_rows), meta


def run_a3_slice(
    histories: Sequence[int],
    *,
    M: int = 2000,
    starts: tuple[int, ...] = H.STARTS,
    horizon: int = H.HORIZON,
    s1_params: S1.S1Params = H.S1_PARAMS,
    rules: J.ToyRules = H.TOY_RULES,
    workers: int = 2,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    part_id = S.PARTS["A3"]
    tasks = [(int(r), int(M), starts, int(horizon), part_id, s1_params, rules) for r in histories]
    rows = _map_workers(_a3_one_history, tasks, workers)
    return pd.DataFrame(rows), {
        "part": "A3",
        "histories_range": [int(histories[0]), int(histories[-1])],
        "M": int(M),
        "seed_roles": ["h3a3_history_null"],
    }


def run_a4_slice(
    histories: Sequence[int],
    *,
    M: int = H.SEEDS,
    starts: tuple[int, ...] = H.STARTS,
    horizon: int = H.HORIZON,
    s1_params: S1.S1Params = H.S1_PARAMS,
    rules: J.ToyRules = H.TOY_RULES,
    workers: int = 2,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    part_id = S.PARTS["A4"]
    tasks = [(int(r), int(M), starts, int(horizon), part_id, s1_params, rules) for r in histories]
    nested = _map_workers(_a4_one_history, tasks, workers)
    flat_rows = [row for grp in nested for row in grp]
    return pd.DataFrame(flat_rows), {
        "part": "A4",
        "histories_range": [int(histories[0]), int(histories[-1])],
        "M": int(M),
        "seed_roles": ["h3a_histories", "h3a_coins"],
        "copy_against_stagger": "not run in H3-A (template does not define overlap yet; section 11)",
    }


def build_final_report(results_dir: Path = RESULTS_DIR) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Combine A1 + A2 pooled counts (54 exact cells) and per-history counts (1080 beside) through `evaluate_laxity_stop`."""
    a1_df = pd.read_csv(Path(results_dir) / "h3a_a1.csv")
    a2_df = pd.read_csv(Path(results_dir) / "h3a_a2.csv")
    pooled = [
        REP.SizeCount(
            str(r["part"]), str(r["null_class"]), str(r["composite"]), str(r["bound"]),
            float(r["level"]), int(r["rejections"]), int(r["n"]),
        )
        for df in (a1_df, a2_df)
        for _, r in df.iterrows()
    ]
    per_hist: list[REP.SizeCount] = []
    for fn in ("h3a_a1_per_history.csv", "h3a_a2_per_history.csv"):
        p = Path(results_dir) / fn
        if p.is_file():
            hdf = pd.read_csv(p)
            per_hist.extend(
                REP.SizeCount(
                    str(r["part"]), str(r["null_class"]), str(r["composite"]), str(r["bound"]),
                    float(r["level"]), int(r["rejections"]), int(r["n"]), history=int(r["history"]),
                )
                for _, r in hdf.iterrows()
            )
    ev = REP.evaluate_laxity_stop(pooled, per_hist)
    return pd.DataFrame(ev["pooled_rows"]), {
        "verdict": ev["verdict"],
        "stop_h3d": ev["stop_h3d"],
        "lax_count": ev["lax_count"],
        "pooled_total": ev["pooled_total"],
        "per_history_count": ev["per_history_count"],
        "family_stop_alpha": ev["family_stop_alpha"],
        "stop_alpha_per_count": ev["stop_alpha_per_count"],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--part", required=True, choices=tuple(SLOT_SPEC.keys()))
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args(argv)

    from extended import results as RES

    part = args.part
    is_report = part == "report"
    pre = check_runtime_gates(part, require_lock=not is_report)
    t0 = time.perf_counter()

    if part == "A1":
        lo, hi = SLOT_SPEC["A1"]["histories"]
        df, hdf, meta = run_a1(histories=range(lo, hi), M=SLOT_SPEC["A1"]["M"], workers=args.workers)
        meta["preconditions"] = pre
        meta["elapsed_s"] = time.perf_counter() - t0
        RES.write_result(
            df, "h3a_a1", script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
            description="H3-A1 same-design nulls (36 pooled counts, E-279/E-285)", parameters=meta,
        )
        RES.write_result(
            hdf, "h3a_a1_per_history", script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
            description="H3-A1 per-history counts beside (720 rows, never deciding, E-279)", parameters=meta,
        )
    elif part == "A2":
        lo, hi = SLOT_SPEC["A2"]["histories"]
        df, hdf, meta = run_a2(histories=range(lo, hi), M=SLOT_SPEC["A2"]["M"], workers=args.workers)
        meta["preconditions"] = pre
        meta["elapsed_s"] = time.perf_counter() - t0
        RES.write_result(
            df, "h3a_a2", script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
            description="H3-A2 exact-centred toy null (18 pooled counts, E-279/E-285)", parameters=meta,
        )
        RES.write_result(
            hdf, "h3a_a2_per_history", script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
            description="H3-A2 per-history counts beside (360 rows, never deciding, E-279)", parameters=meta,
        )
    elif part in ("A3_1", "A3_2"):
        lo, hi = SLOT_SPEC[part]["histories"]
        df, meta = run_a3_slice(range(lo, hi), M=SLOT_SPEC[part]["M"], workers=args.workers)
        meta["preconditions"] = pre
        meta["elapsed_s"] = time.perf_counter() - t0
        RES.write_result(
            df, SLOT_SPEC[part]["out"], script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
            description=f"H3-{part} history null slice (histories {lo}..{hi - 1}, E-279/E-285)", parameters=meta,
        )
    elif part in ("A4_1", "A4_2"):
        lo, hi = SLOT_SPEC[part]["histories"]
        df, meta = run_a4_slice(range(lo, hi), M=SLOT_SPEC[part]["M"], workers=args.workers)
        meta["preconditions"] = pre
        meta["elapsed_s"] = time.perf_counter() - t0
        RES.write_result(
            df, SLOT_SPEC[part]["out"], script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
            description=f"H3-{part} power plants slice (histories {lo}..{hi - 1}, E-279/E-285)", parameters=meta,
        )
    else:
        df, meta = build_final_report(RESULTS_DIR)
        meta["preconditions"] = pre
        meta["elapsed_s"] = time.perf_counter() - t0
        RES.write_result(
            df, "h3a_summary", script=SCRIPT, seed=None, require_seed=False, exploratory=False, prereg_id="H3",
            description="H3-A final laxity stop summary (54 pooled counts, Bonferroni 0.05/54, E-279)", parameters=meta,
        )
        print(f"H3-A verdict: {meta['verdict']} (lax_count={meta['lax_count']}/{meta['pooled_total']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

