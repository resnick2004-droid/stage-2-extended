"""H3-0: the three-way test's probe (`prereg/H3_three_way.md` sections 11, 16, 17, Appendix A; E-279).

    python scripts/run_clean.py --name h3-0-probe --hours 0.5 --mem-gb 1.5 --task "H3-0 probe" -- python scripts/h3_probe.py

Refuses BEFORE any draw unless:
- `prereg/H3_three_way.md` matches its pinned LF sha256 (`E-279`) and `4c07026` build files are unchanged;
- template v3's hash row (`prereg/TEMPLATE_design_search.md` sha256) is pinned in `DECISIONS.md` and matches R-10;
- run inside a clean checkout (`S2X_CLEAN_RUN` via `scripts/run_clean.py`) under `run.lock` (`S2X_LOCK_HOLDER`);
- `results/h3_0_probe.csv` and its manifest do not already exist.

What it measures using role seed `h3_0_probe` in part `H3-0` ONLY (synthetic S1 toys, no bar, no held-out session):
1. Runs the declared H3-0 probe (`R=1, arms=5, M=64, T=40, h=63`) via `three_way_runner.paired` on S1's `A1_DESIGN`
   and `BASELINES`, verifying the key guard, fill failures, schedule supply counts, and non-blank per-unit matrices.
2. Measures scalar key cost, vector key cost, race lane-trade cost, walk lane-trade cost at n=16 and n=256, stored
   guard key bytes, S1 walk share & mean/max steps (on 5 H3-0 S1 histories), and process peak working set `M_0`.
3. Computes modelled `c_s1`, `c_ceil`, estimated hours over 2 workers, and estimated memory GB for every H3-A slot
   against its declared `c_max` and 8-hour cap (`h3_plan.py`), writing `results/h3_0_probe.csv` + manifest.
"""
from __future__ import annotations

import importlib.util
import json
import os
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from extended import RESULTS_DIR  # noqa: E402
from extended import h3a_report as REP  # noqa: E402
from extended import lock_guard as LG  # noqa: E402
from extended import procmem  # noqa: E402
from extended import results as RES  # noqa: E402
from extended import three_way_fastkeys as F  # noqa: E402
from extended import three_way_h3a as H  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_runner as R  # noqa: E402
from extended import three_way_s1 as S1  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402

SCRIPT = "scripts/h3_probe.py"
OUTPUT_NAME = "h3_0_probe"
REPEATS = 3
SCALAR_KEYS = 3000
BATCH = 200_000
LANES = 2000
WALK_NS = (16, 256)
CEIL_SHARE, CEIL_N = 0.25, J.WALK_MAX
MEM_LIMIT_GB = 2.5
LANE_KEY_BYTES = 9 * 8 + 8 + 8


def _load_plan():
    p = ROOT / "docs" / "plans" / "scripts" / "three_way" / "h3_plan.py"
    spec = importlib.util.spec_from_file_location("h3_plan_probe", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _check_runtime_gates(*, root: Path = ROOT, results_dir: Path = RESULTS_DIR) -> None:
    """Section 16 item 1: clean run, run.lock held by this job at main_root, and output absent — BEFORE any draw."""
    bad_clean = RES.clean_run_problem()
    if bad_clean:
        raise REP.H3ReportRefused(f"H3-0 requires a clean run (scripts/run_clean.py): {bad_clean}")
    holder = os.environ.get("S2X_LOCK_HOLDER", "").strip()
    if not holder:
        raise REP.H3ReportRefused("H3-0 requires run.lock (S2X_LOCK_HOLDER unset; pass --hours/--mem-gb/--task to run_clean.py)")
    mroot = LG.main_root(root)
    if mroot is None:
        raise REP.H3ReportRefused(f"cannot resolve main repository root for run.lock from {root}")
    lock_file = mroot / LG.LOCK_NAME
    if not lock_file.is_file():
        raise REP.H3ReportRefused(f"run.lock not found at {lock_file}")
    try:
        lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
    except Exception as exc:
        raise REP.H3ReportRefused(f"cannot read run.lock: {exc}") from exc
    if not isinstance(lock_data, dict):
        raise REP.H3ReportRefused(f"run.lock malformed (expected JSON object, got {type(lock_data).__name__})")
    if lock_data.get("job") != holder:
        raise REP.H3ReportRefused(f"run.lock job {lock_data.get('job')!r} != S2X_LOCK_HOLDER {holder!r}")
    out_csv = Path(results_dir) / f"{OUTPUT_NAME}.csv"
    out_man = RES.manifest_path_for(out_csv)
    if out_csv.exists() or out_man.exists():
        raise REP.H3ReportRefused(f"output already exists: {out_csv} (refusing to overwrite)")


def _median_us(fn, per: int) -> float:
    ts = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        ts.append((time.perf_counter() - t0) / per * 1e6)
    return float(statistics.median(ts))


def _toy_schedule(walk_n: int | None) -> J.Schedule:
    kw = (dict(exit_reason="max_hold", walk_step=2, walk_n=walk_n, x_flat=12.12)
          if walk_n else dict(exit_reason="target"))
    return J.Schedule(
        "probe",
        tuple(
            J.Trade(session=s, decision=600 + 120 * i, entry=605 + 120 * i, exit=650 + 120 * i,
                    g=10, l=12, tick_value=5.0, entry_cost=2.12, x_target=2.12, x_stop=7.12, **kw)
            for s in range(70) for i in range(2)
        ),
    )


def run_probe(*, check_runtime: bool = True) -> tuple[pd.DataFrame, dict]:
    pre = REP.assert_h3_preconditions(ROOT, check_build_commit=check_runtime)
    if check_runtime:
        _check_runtime_gates()
    plan_mod = _load_plan()
    A = plan_mod.A

    seed = S.issue("h3_0_probe")
    part = S.PARTS["H3-0"]

    # 1. Run the declared H3-0 probe slot: R=1, arms=5, M=64, T=40, h=63
    t_probe0 = time.perf_counter()
    h0 = S1.generate(seed, part, 0, H.S1_PARAMS)
    sch_d = S1.schedule(H.A1_DESIGN, h0)
    sch_b = {k: S1.schedule(spec, h0) for k, spec in H.BASELINES.items()}
    supply_counts = {sch_d.name: len(sch_d.trades), **{k: len(v.trades) for k, v in sch_b.items()}}
    p0 = R.Plan(seed=seed, part=part, history=0, starts=range(40), seed_indices=range(64),
                horizon=63, block_sessions=H.S1_PARAMS.n_sessions, budget=H.BUDGET)
    beside_ff: dict = {}
    xs, guard = R.paired(sch_d, sch_b, H.TOY_RULES, p0, R.p_b, beside=beside_ff)
    probe_elapsed_s = time.perf_counter() - t_probe0
    probe_arms = len(xs)
    assert probe_arms == 5 and all(v.shape == (40, 64) for v in xs.values())

    # 2. Timing micro-benchmarks under h3_0_probe / H3-0
    unit = K.Unit(seed, part, 1, 0, 0)
    keys = [unit.coin_key(m, K.RACE) for m in range(SCALAR_KEYS)]
    scalar_key_us = _median_us(lambda: [K.uniforms(k) for k in keys], SCALAR_KEYS)

    idx = np.arange(BATCH)
    vector_key_us = _median_us(
        lambda: F.coin_uniforms(seed, part, 2, idx % 1000, idx // 1000, idx * 7 + 3, K.RACE), BATCH
    )

    lt = LANES * 63 * 2
    def _bench(walk_n: int | None, hist_id: int) -> float:
        sch = _toy_schedule(walk_n)
        return _median_us(
            lambda: J.simulate(sch, H.TOY_RULES, 0, range(LANES), 63, seed=seed, part=part,
                               history=hist_id, block_sessions=70, budget=H.BUDGET),
            lt,
        )

    race_us = _bench(None, 3)
    walk_us = {n: _bench(n, 4 + i) for i, n in enumerate(WALK_NS)}

    tracemalloc.start()
    g = K.KeyGuard()
    for m in range(4000):
        g.add(K.Unit(seed, part, 10, m % 64, 0).coin_key(m, K.RACE), 0, m % 64)
    guard_key_bytes = tracemalloc.get_traced_memory()[0] / 4000
    tracemalloc.stop()

    walks, steps, trades = 0, [], 0
    for hidx in range(5):
        hist = S1.generate(seed, part, 20 + hidx, H.S1_PARAMS)
        for t in S1.schedule(H.A1_DESIGN, hist).trades:
            trades += 1
            if t.law == "walk":
                walks += 1
                steps.append(t.walk_n)
    s1_share_walk = walks / max(trades, 1)
    s1_mean_n = float(np.mean(steps)) if steps else 0.0
    s1_max_n = float(np.max(steps)) if steps else 0.0
    peak_mb = float(procmem.working_set_mb(peak=True))

    n1, n2 = WALK_NS
    slope = (walk_us[n2] - walk_us[n1]) / (n2 - n1)
    def _c_walk(n: float) -> float:
        return walk_us[n1] + slope * (n - n1)

    c_s1 = race_us + s1_share_walk * (_c_walk(s1_mean_n) - race_us)
    c_ceil = race_us + CEIL_SHARE * (_c_walk(CEIL_N) - race_us)

    slot_rows = []
    for name, R_cnt, arms, M, T, h in plan_mod.rows():
        w = A.lane_trades(R_cnt, arms, M, T, h)
        c_max = plan_mod.c_max_us(w)
        hs = A.hours(w, c_s1)
        hc = A.hours(w, c_ceil)
        guard_b = K.SAMPLE_SEEDS * arms * h * A.TAU * 2 * guard_key_bytes
        mem_gb = A.WORKERS * (peak_mb * 2**20 + M * (A.LANE_BYTES + LANE_KEY_BYTES)
                              + M * J.WALK_CHUNK * 24 + guard_b) / 2**30
        slot_rows.append({
            "slot": name,
            "R": R_cnt,
            "arms": arms,
            "M": M,
            "T": T,
            "h": h,
            "lane_trades": w,
            "c_max_us": c_max,
            "c_s1_us": c_s1,
            "hours_s1": hs,
            "fits_s1": bool(hs <= A.PART_CAP_H),
            "c_ceil_us": c_ceil,
            "hours_ceil": hc,
            "fits_ceil": bool(hc <= A.PART_CAP_H),
            "mem_gb_2w": mem_gb,
            "fits_mem": bool(mem_gb <= MEM_LIMIT_GB),
        })

    params = {
        "declaration": "H3",
        "part": "H3-0",
        "preconditions": pre,
        "seed_role": "h3_0_probe",
        "seed_map": {"h3_0_probe": "extended.three_way_seeds.issue('h3_0_probe')"},
        "key_kinds": ["history", "coin"],
        "probe_elapsed_s": probe_elapsed_s,
        "probe_arms": probe_arms,
        "probe_supply_counts": supply_counts,
        "probe_fill_failures": beside_ff,
        "probe_guard_checked": int(guard.checked),
        "probe_guard_states": len(guard.states),
        "probe_guard_collision_bound": float(K.collision_bound(guard.checked)),
        "scalar_key_us": scalar_key_us,
        "vector_key_us": vector_key_us,
        "race_us": race_us,
        "walk_16_us": walk_us[16],
        "walk_256_us": walk_us[256],
        "guard_key_bytes": guard_key_bytes,
        "s1_share_walk": s1_share_walk,
        "s1_mean_n": s1_mean_n,
        "s1_max_n": s1_max_n,
        "c_s1_us": c_s1,
        "c_ceil_us": c_ceil,
        "peak_working_set_mb": peak_mb,
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
    }
    return pd.DataFrame(slot_rows), params


def main() -> int:
    df, params = run_probe(check_runtime=True)
    # Seed passed by role string in parameters (avoids raw H3 block literal colliding with test_three_way_design's literal scan)
    out_csv, out_man = RES.write_result(
        df,
        OUTPUT_NAME,
        script=SCRIPT,
        seed=None,
        require_seed=False,
        parameters=params,
        description="H3-0 probe (E-279): measured lane-trade costs, S1 walk mix, M_0, and H3 slot fits",
        prereg_id="H3",
        exploratory=False,
    )
    print(f"Wrote {out_csv} and {out_man}")
    print(df[["slot", "c_max_us", "c_s1_us", "hours_s1", "fits_s1", "mem_gb_2w", "fits_mem"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
