"""Q-170 and Wave 3.2's corrective cycle 1 (the red team's m-5): the declared generator's cost on this machine, scalar
and vectorised, the runner's own cost a lane-trade with **the walk's term**, and every H3 heavy slot's hours and memory
at those costs -- a timing on synthetic toys, no bar, no outcome, no result file (it prints; nothing is written).

What it measures (each the median of `REPEATS` timings):
- **the key, scalar** -- the declared law one key at a time (`three_way_keys.uniforms`), the old runner's path;
- **the key, vectorised** -- `three_way_fastkeys.coin_uniforms` over `BATCH` keys, divided by the keys;
- **the runner's race lane-trade** -- `three_way_journey.simulate` (which reads its uniforms through the vectorised law)
  on a race toy of `LANES` seeds, 63 sessions and two trades a session, guard off, divided by its lane-trades;
- **the runner's walk lane-trade at n steps** -- the same on a walk toy at n = `WALK_NS`; the walk's cost is modelled
  c_walk(n) = a + b n, fitted to the two;
- **the process's peak working set** (`extended.procmem`), an upper bound on M_0 for this code.

**The cost model** (the red team's remedy): c = c_race + share_walk x (c_walk(n-bar) - c_race), with share_walk and
n-bar read from the schedules of H3-A's declared design on S1 at its declared values (`extended/three_way_h3a.py`), on
histories of the tests' seed. For H3-D and H7 the walks of NQ are H4's to measure; two readings are printed: S1's mix
as a stand-in, and a ceiling (share `CEIL_SHARE`, `CEIL_N` steps).

**Memory a worker:** M_0 plus one start's M lanes of one arm (`three_way_arith.LANE_BYTES`), the walk's uniform matrix
(M x `three_way_journey.WALK_CHUNK` x 24 bytes: the walk is read in chunks), and the guard's sample (`three_way_keys.SAMPLE_SEEDS` seeds x arms x
h x four trades a session x two keys at the measured bytes a stored key); two workers against `MEM_LIMIT_GB`.

    python docs/plans/scripts/three_way/h3_cost.py
"""
from __future__ import annotations

import importlib.util
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from extended import procmem  # noqa: E402
from extended import three_way_fastkeys as F  # noqa: E402
from extended import three_way_h3a as H  # noqa: E402
from extended import three_way_journey as J  # noqa: E402
from extended import three_way_keys as K  # noqa: E402
from extended import three_way_s1 as S1  # noqa: E402
from extended import three_way_seeds as S  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_for_h3_cost", HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PLAN = _load("h3_plan")
A = PLAN.A
REPEATS = 3
SCALAR_KEYS = 3000
BATCH = 200_000
LANES = 2000
WALK_NS = (16, 256)
CEIL_SHARE, CEIL_N = 0.25, 2048
MEM_LIMIT_GB = 2.0
LANE_KEY_BYTES = 9 * 8 + 8 + 8


def _median(f, per: int) -> float:
    ts = []
    for _ in range(REPEATS):
        t = time.perf_counter()
        f()
        ts.append((time.perf_counter() - t) / per * 1e6)
    return statistics.median(ts)


def _toy(walk_n: int | None) -> J.Schedule:
    kw = (dict(exit_reason="max_hold", walk_step=2, walk_n=walk_n, x_flat=12.12) if walk_n
          else dict(exit_reason="target"))
    return J.Schedule("probe", tuple(J.Trade(session=s, decision=600 + 120 * i, entry=605 + 120 * i,
                                             exit=650 + 120 * i, g=10, l=12, tick_value=5.0, entry_cost=2.12,
                                             x_target=2.12, x_stop=7.12, **kw)
                                     for s in range(70) for i in range(2)))


def measure() -> dict[str, float]:
    seed = S.issue("h3_0_probe")
    part = S.PARTS["H3-0"]
    unit = K.Unit(seed, part, 0, 0, 0)
    keys = [unit.coin_key(m, K.RACE) for m in range(SCALAR_KEYS)]
    out = {"scalar_key_us": _median(lambda: [K.uniforms(k) for k in keys], SCALAR_KEYS)}
    idx = np.arange(BATCH)
    out["vector_key_us"] = _median(lambda: F.coin_uniforms(seed, part, 0, idx % 1000, idx // 1000, idx * 7 + 3,
                                                           K.RACE), BATCH)
    rules = H.TOY_RULES
    lt = LANES * 63 * 2

    def run(walk_n):
        sch = _toy(walk_n)
        return _median(lambda: J.simulate(sch, rules, 0, range(LANES), 63, seed=seed, part=part, history=0,
                                          block_sessions=70, budget=H.BUDGET), lt)

    out["race_us"] = run(None)
    for n in WALK_NS:
        out[f"walk_{n}_us"] = run(n)
    tracemalloc.start()
    g = K.KeyGuard()
    for m in range(4000):
        g.add(K.Unit(seed, part, 0, m % 64, 0).coin_key(m, K.RACE), 0, m % 64)
    out["guard_key_bytes"] = tracemalloc.get_traced_memory()[0] / 4000
    tracemalloc.stop()
    walks, steps, trades = 0, [], 0
    for hidx in range(5):
        hist = S1.generate(S.issue("tests"), S.PARTS["tests"], 900 + hidx, H.S1_PARAMS)
        for t in S1.schedule(H.A1_DESIGN, hist).trades:
            trades += 1
            if t.law == "walk":
                walks += 1
                steps.append(t.walk_n)
    out["s1_share_walk"] = walks / max(trades, 1)
    out["s1_mean_n"] = float(np.mean(steps)) if steps else 0.0
    out["s1_max_n"] = float(np.max(steps)) if steps else 0.0
    out["peak_mb"] = procmem.working_set_mb(peak=True)
    return out


def c_walk(m: dict[str, float], n: float) -> float:
    (n1, n2) = WALK_NS
    b = (m[f"walk_{n2}_us"] - m[f"walk_{n1}_us"]) / (n2 - n1)
    return m[f"walk_{n1}_us"] + b * (n - n1)


def report(m: dict[str, float]) -> str:
    c_s1 = m["race_us"] + m["s1_share_walk"] * (c_walk(m, m["s1_mean_n"]) - m["race_us"])
    c_ceil = m["race_us"] + CEIL_SHARE * (c_walk(m, CEIL_N) - m["race_us"])
    out = [f"measured on this machine (median of {REPEATS}; other workers' jobs running): the key scalar"
           f" {m['scalar_key_us']:.2f} us, vectorised {m['vector_key_us']:.3f} us; the runner's race lane-trade"
           f" {m['race_us']:.3f} us; its walk lane-trade {m[f'walk_{WALK_NS[0]}_us']:.3f} us at n={WALK_NS[0]} and"
           f" {m[f'walk_{WALK_NS[1]}_us']:.3f} us at n={WALK_NS[1]}; a stored guard key {m['guard_key_bytes']:.0f} B;"
           f" peak working set {m['peak_mb']:.0f} MB",
           f"S1 at H3-A's declared values: share of walks {m['s1_share_walk']:.3f}, mean steps {m['s1_mean_n']:.0f},"
           f" longest {m['s1_max_n']:.0f}; c a lane-trade: S1's mix {c_s1:.3f} us, the ceiling (share {CEIL_SHARE},"
           f" n={CEIL_N}) {c_ceil:.3f} us; the scalar key's old path would add {m['scalar_key_us']:.1f} us a key",
           "slot | lane-trades | c_max us | hours at S1's mix | fits | hours at the ceiling | fits | memory GB (2"
           " workers) | fits"]
    for name, R, arms, M, T, h in PLAN.rows():
        w = A.lane_trades(R, arms, M, T, h)
        hs, hc = A.hours(w, c_s1), A.hours(w, c_ceil)
        guard = K.SAMPLE_SEEDS * arms * h * A.TAU * 2 * m["guard_key_bytes"]
        mem = A.WORKERS * (m["peak_mb"] * 2 ** 20 + M * (A.LANE_BYTES + LANE_KEY_BYTES) + M * J.WALK_CHUNK * 24
                           + guard) / 2 ** 30
        ok = lambda x: "yes" if x <= A.PART_CAP_H else "NO"           # noqa: E731
        out.append(f"  {name:<30} | {w:.3e} | {PLAN.c_max_us(w):6.2f} | {hs:7.2f} | {ok(hs)} | {hc:8.2f} | {ok(hc)}"
                   f" | {mem:.2f} | {'yes' if mem <= MEM_LIMIT_GB else 'NO'}")
    return "\n".join(out)


def main() -> None:
    print(report(measure()))


if __name__ == "__main__":
    main()
