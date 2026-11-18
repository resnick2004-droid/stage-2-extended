"""F-03's cost probe (E-129 item 1): each stage of A0, run 1 and run 2 measured on synthetic data of the window's real
size -- the real calendars (2020-01-02 .. 2023-12-29 and 2024-01-02 .. 2026-07-16), a realistic day-kind mix, P-16's
admitted marks and registered configuration (`opening_population.p16_inputs`, `admitted_marks`), every start, the gate's
500 paths, the declared replication counts. Synthetic bars only (`extended/synthetic_bars.py`, `[SEED_TESTS, 1600, ...]`),
never the licensed data; nothing is written but the work folder's own pickles. One unit a process, run one at a time:

    python tests/fo_cost_probe.py <repository root> <work folder> <unit> [count]

Units: `store` (the synthetic window: bars, day kinds); `span_choice`, `span_judged` (the population walk, every mark at
every table R, both sides, and its trades); `states` (the choice grid, s1, s2, u3's walk-forward, A3's 200 cuts and its
two further checks); `replay_choice`, `replay_judged` (one every-start U1 replay, the verdict arm, with the family's
recorder and a waiting class); `k0` (one K0 form at 200,000); `a10` (A10's first check, 2,000 selections a class and
share); `stage_b` (stage B's 2,000-draw bootstrap, three cells); `gate` (one gate campaign at 500 paths with the waiting
class in index mode); `b2` (B2 at `count` replicates of one line on the judged layout); `a10_b2` (one A10 consequence
B2 run at 20,000 inner draws on the choice layout). Each prints one JSON line: seconds and the process's peak working
set during the unit, sampled every 0.1 s (Windows `GetProcessMemoryInfo`), above the baseline before it.
"""
from __future__ import annotations

import ctypes
import json
import pickle
import sys
import threading
import time
from datetime import date
from pathlib import Path

REPO, WORK, UNIT = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
COUNT = int(sys.argv[4]) if len(sys.argv) > 4 else None
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "identity")):
    sys.path.insert(0, _p)
KEY = (20261988, 1600)                      # section 16's test block, the builder's key 1600: this probe


class _PMC(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("a", ctypes.c_size_t), ("b", ctypes.c_size_t),
                ("c", ctypes.c_size_t), ("d", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]


def working_set() -> int:
    c = _PMC()
    c.cb = ctypes.sizeof(_PMC)
    k32 = ctypes.windll.kernel32
    k32.GetCurrentProcess.restype = ctypes.c_void_p                  # a 64-bit pseudo-handle, never truncated
    k32.K32GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    if not k32.K32GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
        raise OSError("GetProcessMemoryInfo failed")
    return int(c.WorkingSetSize)


class Meter:
    """The unit's seconds and its peak working set (sampled) above the baseline taken when it starts."""

    def __enter__(self):
        self.base = working_set()
        self.peak = self.base
        self._stop = False

        def run():
            while not self._stop:
                self.peak = max(self.peak, working_set())
                time.sleep(0.1)
        self._t = threading.Thread(target=run, daemon=True)
        self._t.start()
        self.t0 = time.time()
        return self

    def __exit__(self, *a):
        self.seconds = time.time() - self.t0
        self._stop = True
        self._t.join()
        self.peak = max(self.peak, working_set())


def dump(name, obj):
    with open(WORK / f"{name}.pkl", "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load(name):
    with open(WORK / f"{name}.pkl", "rb") as f:
        return pickle.load(f)


def kinds_of(days):
    import numpy as np

    rng = np.random.default_rng([*KEY, 9])
    k = np.array(["b" if (d.weekday() == 4 and d.day <= 7) else "n" for d in days], dtype=object)
    for y in sorted({d.year for d in days}):
        idx = [i for i, d in enumerate(days) if d.year == y and k[i] == "n"]
        for kind, m in (("o", 8), ("e", 3), ("x", 1)):
            pick = rng.choice(idx, size=min(m, len(idx)), replace=False)
            k[pick] = kind
            idx = [i for i in idx if i not in set(int(x) for x in pick)]
    return {d.isoformat(): str(x) for d, x in zip(days, k)}


def unit_store():
    from extended import features as F
    from extended import synthetic_bars as sb

    out = {}
    for name, (a, b, s) in {"choice": (date(2020, 1, 2), date(2023, 12, 29), 0),
                            "judged": (date(2024, 1, 2), date(2026, 7, 16), 1)}.items():
        from extended import opening_states as OS

        parts = []
        for y in range(a.year, b.year + 1):                  # a year at a time: the generator's peak stays small
            bars = sb.generate(sb.Spec(max(a, date(y, 1, 1)), min(b, date(y, 12, 31)), seed=[*KEY, s, y],
                                       vol_scale=10.0, holidays=frozenset(), early_closes=frozenset(),
                                       base_price=13000.0 + 1000.0 * (y - 2020)))
            parts.append(F.grid(bars))
            del bars
        g = OS.concat_grids(parts)
        del parts
        dump(f"grid_{name}", g)
        out[name] = {"sessions": len(g.days)}
        dump(f"kinds_{name}", kinds_of(g.days))
    return out


def arrays(g):
    import numpy as np

    return {d.isoformat(): tuple(np.r_[np.nan, X[i][:1330]] for X in (g.O, g.H, g.L, g.C)) for i, d in enumerate(g.days)}


def unit_span(name):
    import pandas as pd

    from extended import opening_population as OP
    from extended import walker as W

    g, kinds = load(f"grid_{name}"), load(f"kinds_{name}")
    other = load(f"kinds_{'judged' if name == 'choice' else 'choice'}")
    arr = arrays(g)
    del g
    tab = pd.DataFrame({"date": sorted(kinds), "day_kind": [kinds[d] for d in sorted(kinds)]})
    all_dates = sorted(set(kinds) | set(other))
    extra = {"extra_rules": {"be_both": W.STAGE2_BE_BOTH}} if name == "judged" else {}
    with Meter() as m:
        sp = OP.build_span(tab["date"].iloc[0], tab["date"].iloc[-1], all_dates, arrays_for=lambda c: arr.__getitem__,
                           days_table=tab, admitted=OP.admitted_marks(), log=lambda x: None, **extra)
    dump(f"span_{name}", sp)
    return m, {"offers": int(len(sp.population)), "population": int(sp.population["population"].sum()),
               "trades": int(len(sp.trades))}


def unit_states():
    import numpy as np

    import fo_opening as FO
    from extended import opening_population as OP
    from extended import opening_states as OS
    from extended import opening_stats as ST

    g, kinds = load("grid_choice"), load("kinds_choice")
    walked = [i for i, d in enumerate(g.days) if kinds[d.isoformat()] in OP.WALKED_KINDS]
    from extended import features as F
    gw = F.Grid([g.days[i] for i in walked], g.contract[walked], g.O[walked], g.H[walked], g.L[walked], g.C[walked],
                g.V[walked])
    del g
    with Meter() as m:
        st = OS.compute(gw)
        report = {i for i, d in enumerate(st.days) if kinds[d.isoformat()] == "b"}
        cuts = FO.a3_cuts(gw, st, FO.A3_CUTS, report)
        a3 = OS.invariance_problems(gw, st, cuts, ST.SEED_SHIFT)
        defined = [i for i in range(len(st.days)) if np.isfinite(st.share("s1")[i]).any()]
        a3w = OS.window_problems(gw, st, defined[:: max(1, len(defined) // 30)][:30], ST.SEED_SHIFT)
    dump("states_choice", {"frame": st.frame(), "forecast": st.forecast})
    return m, {"cuts": len(cuts), "a3_problems": len(a3) + len(a3w), "sessions": len(st.days)}


def layout_choice():
    from extended import opening_states as OS
    from extended import opening_stats as ST

    sp, s = load("span_choice"), load("states_choice")
    kinds = load("kinds_choice")
    pop = sp.population.merge(s["frame"], on=["date", "slot"], how="left", validate="many_to_one")
    for c in OS.BUILT:
        pop[f"in_{c}"] = pop[f"in_{c}"].astype("boolean").fillna(False).astype(bool) & pop["population"].astype(bool)
    cal = sorted(d for d in kinds if d >= "2021-01-04")
    spp = pop[pop["date"] >= "2021-01-04"].reset_index(drop=True)
    L = ST.layout(spp, cal, kinds=kinds, values=("c", "c_close", "rl", "rs"), flags=[f"in_{c}" for c in OS.BUILT])
    return L, sp


def unit_replay(name):
    import numpy as np

    import fo_opening as FO
    from extended import opening_population as OP
    from extended import opening_wait as OW

    sp, kinds = load(f"span_{name}"), load(f"kinds_{name}")
    P = OP.p16_inputs()
    days = sorted(kinds)
    with Meter() as m:
        jobs = FO.u1_job(sp.trades, days, P)
        job = jobs["verdict"]
        ids = FO.offer_ids_of(sp.trades, days, job["blocks"])
        starts = [i for i, d in enumerate(job["dates"]) if str(d) >= ("2021-01-04" if name == "choice" else "2024")]
        if COUNT:
            starts = starts[:: max(1, len(starts) // COUNT)][:COUNT]
        rng = np.random.default_rng([*KEY, 2])
        flags = [rng.random(len(b)) < 1 / 3 for b in job["blocks"]]
        cls = OW.waiting_class(OW.WaitSpec.for_blocks("probe", job["blocks"], flags))
        outs, rec = FO.replay("fo_probe", job, starts, 1, cls, ids)
    return m, {"starts": len(starts), "openings": int(len(OW.openings(rec, "fo_probe", "verdict", "off")))}


def unit_k0():
    from extended import opening_run as R
    from extended import opening_stats as ST

    L, _ = layout_choice()
    sel = L.flags["in_s1"] & L.population
    with Meter() as m:
        v = ST.k0_family(sel.sum(axis=1), L.population.sum(axis=1), "nested", 657, R.LEVEL, 0, 0, COUNT or 200_000)
    return m, {"replications": COUNT or 200_000, "lax": bool(v.lax)}


def unit_a10():
    from extended import opening_stats as ST

    L, _ = layout_choice()
    y = ST.centred(L, "c", L.population)
    with Meter() as m:
        t = ST.a10(L, y, selections=COUNT or 2000)
    return m, {"rows": int(len(t))}


def unit_a9():
    from extended import opening_run as R
    from extended import opening_stats as ST

    L, _ = layout_choice()
    y = ST.centred(L, "c", L.population)
    with Meter() as m:
        r = ST.a9_mdl(L, y, L.flags["in_s1"], 657, R.LEVEL)
    return m, {"windows": r["windows"]}


def unit_states_frozen():
    from extended import features as F
    from extended import opening_population as OP
    from extended import opening_states as OS

    gc, kc = load("grid_choice"), load("kinds_choice")
    gj, kj = load("grid_judged"), load("kinds_judged")
    s = load("states_choice")
    wc = [i for i, d in enumerate(gc.days) if kc[d.isoformat()] in OP.WALKED_KINDS][-300:]
    wj = [i for i, d in enumerate(gj.days) if kj[d.isoformat()] in OP.WALKED_KINDS]
    g = OS.concat_grids([F.Grid([x.days[i] for i in w], x.contract[w], x.O[w], x.H[w], x.L[w], x.C[w], x.V[w])
                         for x, w in ((gc, wc), (gj, wj))])
    del gc, gj
    with Meter() as m:
        st = OS.compute(g, frozen=s["forecast"].final, test_years=())
    return m, {"sessions": len(st.days)}


def unit_stage_b():
    from extended import opening_stats as ST

    L, _ = layout_choice()
    with Meter() as m:
        b = ST.stage_b_bootstrap(L, "c", {c: L.flags[f"in_{c}"] for c in ("s1", "s2", "u3")}, draws=COUNT or 2000)
    return m, {"q_B": float(b["q_B"])}


def unit_gate():
    import numpy as np

    import fo_opening as FO
    from extended import opening_population as OP
    from extended import opening_stats as ST
    from extended import opening_wait as OW

    sp, kinds = load("span_judged"), load("kinds_judged")
    P = OP.p16_inputs()
    days = sorted(kinds)
    rng = np.random.default_rng([*KEY, 3])

    def make(blocks):
        return OW.waiting_class(OW.WaitSpec.for_index("probe_gate", [rng.random(len(b)) < 1 / 3 for b in blocks],
                                                      blocks=blocks))
    with Meter() as m:
        rows, _ = FO.gate_campaign(sp.trades, days, P, seed=ST.SEED_GATE, n_paths=COUNT or 500, workers=1, cls=make)
    return m, {"paths": COUNT or 500, "rows": int(len(rows))}


def unit_b2():
    import numpy as np

    from extended import opening_run as R
    from extended import opening_stats as ST

    L, _ = layout_choice()
    sp, kinds = load("span_judged"), load("kinds_judged")
    pop = sp.population
    cal = sorted(kinds)
    Lj = ST.layout(pop, cal, kinds=kinds, values=("c",))
    yc = ST.centred(L, "c", L.population)
    k = {m_: i for i, m_ in enumerate(L.marks)}
    ycj = np.full((L.n, len(Lj.marks)), np.nan)
    for j, m_ in enumerate(Lj.marks):
        if m_ in k:
            ycj[:, j] = yc[:, k[m_]]
    W1 = (Lj.population & (np.random.default_rng([*KEY, 4]).random(Lj.population.shape) < 1 / 3)).astype(float)
    inp = ST.B2Inputs(ycj, L.kind, Lj.kind, Lj.group, Lj.exists & Lj.population, W1, Lj.population.astype(float))
    n = COUNT or 2000
    with Meter() as m:
        ST.b2_quantiles(inp, 0.02, R.LEVEL, ST.LINE_C1, replicates=n, prefix=(*KEY, 5))
    return m, {"replicates": n, "judged_sessions": Lj.n, "marks": len(Lj.marks), "seconds_per_replicate": None}


def unit_a10_b2():
    from extended import opening_stats as ST

    L, _ = layout_choice()
    with Meter() as m:
        r = ST.a10_consequence(L, "c", "window", 0.0, selections=COUNT or 3, inner=20_000, shortcut=False)
    return m, {"b2_runs": r.b2_runs, "inner": 20_000}


if __name__ == "__main__":
    from extended import use_vendored_stage2

    use_vendored_stage2()
    WORK.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if UNIT == "store":
        info, m = unit_store(), None
    else:
        fn = {"span_choice": lambda: unit_span("choice"), "span_judged": lambda: unit_span("judged"),
              "states": unit_states, "replay_choice": lambda: unit_replay("choice"),
              "replay_judged": lambda: unit_replay("judged"), "k0": unit_k0, "a10": unit_a10,
              "stage_b": unit_stage_b, "a9": unit_a9, "states_frozen": unit_states_frozen, "gate": unit_gate, "b2": unit_b2, "a10_b2": unit_a10_b2}[UNIT]
        m, info = fn()
    rec = {"unit": UNIT, "count": COUNT, **info, "wall_seconds": round(time.time() - t0, 1)}
    if m is not None:
        rec.update({"seconds": round(m.seconds, 1), "baseline_mb": round(m.base / 2**20),
                    "peak_mb": round(m.peak / 2**20), "peak_rise_mb": round((m.peak - m.base) / 2**20)})
        if UNIT in ("b2",):
            rec["seconds_per_replicate"] = round(m.seconds / rec["replicates"], 5)
    print(json.dumps(rec, default=str))
