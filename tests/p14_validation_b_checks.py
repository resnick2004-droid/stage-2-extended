"""Q-18b: `extended/p14_stress_b.py` and `scripts/p14_validation_b.py` on synthetic data -- no bars, no atlas, no engine
run. Run by `tests/test_p14_validation_b.py` in a process of its own (it puts the vendored tree on `sys.path`).

    python tests/p14_validation_b_checks.py          # every check: 'HOLDS: <name>' for each, exit 0; 'FAILS: <name>' exit 3

* `engine_run`: `Q.Engine._run` keeps every column the vendored `Engine._run` keeps, value for value, adds `EXTRA` and
  each arm's per-path required bankroll (the hook's own `path_values`), records each run by label; `run` is the
  vendored method underneath (the labels, the cache).
* `ruin`: the ruin figures recomputed by hand -- the share of paths above a bankroll, the run's own p90 and the
  reference's, the engine's ruin and the bankroll distribution carried, references resolved by label.
* `a2_source` / `a2_rows`: `Q.part_a2` is the vendored `part_a2`'s text with only its seed replaced; with the engine's
  path functions replaced by deterministic fakes, `seed=V.SEED_A2` gives the vendored part's rows exactly, another
  seed draws other paths (`path_seeds(seed)`), and the real-order side is the same.
* `slip_b`: `Q.part_slip_b` runs, per D-583 arm, the verdict-level run (the existing label), the 0.05-level run and the
  twin, with the right trades, e and bounds (the twin's outcomes less the arm's own e, e and bound zero), slices at the
  0.05 bound; its rows and `slip_readings` (D-583's reading per level) recomputed here, a family turning at each level.
* `slices`: the summary and line pickers and their identity checks pass on equal rows and catch a changed one;
  `slice_campaign`'s engine arguments.
* `file_identity`: the re-made rows against a file written by `write_result` -- equal rows pass, a last-digit change,
  a flag, a blank and a text change are each caught.
* `assumptions`: each standing assumption E-125 lists is a row read from the engine call.
* `runner`: the runner's label wiring, the old ledger's runs, the twin check, the provenance line, its refusals.
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import math
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import p14_stress_b as Q  # noqa: E402  (puts the vendored tree on sys.path)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

VS, V, ps16, X = Q.VS, Q.V, Q.ps16, Q.X


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = _load("v1_adapter_checks", "tests/v1_adapter_checks.py")      # the synthetic subject and engine of Q-18's checks


def fake_paths(seed: int, n: int = 40, days: int = 60) -> list:
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        cash = np.concatenate([[10000.0], 10000.0 + np.cumsum(rng.normal(5, 120, days))])
        pays = sorted(rng.choice(days, int(rng.integers(0, 4)), replace=False).tolist())
        out.append(SimpleNamespace(path=SimpleNamespace(
            cash_series=cash.tolist(), initial_bankroll=10000.0, days_to_first_payout=(pays[0] if pays else None),
            payout_gaps=[b - a for a, b in zip(pays, pays[1:])])))
    return out


# ------------------------------------------------------------------------------------------------ engine_run


def check_engine_run() -> list[str]:
    from propedge.campaign import gate

    sub = A.subject("P14", eras=False, flagged=False)
    calls = []

    def fake_run_gate(blocks, workers, path_hook, **kw):
        calls.append(kw)
        rows = []
        for k, shift in enumerate(("lower_bound", "point")):
            out = path_hook(shift, 0.0, fake_paths(100 + k))
            row = {"shift": shift, "enforcement_p": 0.0, **out}
            for i, c in enumerate(dict.fromkeys(VS.READ + VS.BESIDE + VS.IDENT_COLS + Q.EXTRA)):
                row.setdefault(c, float(i) + 0.25 * k + 0.001 * len(kw))
            row["not_kept"] = 1.0
            rows.append(row)
        return pd.DataFrame(rows), None

    real = gate.run_gate
    gate.run_gate = fake_run_gate
    try:
        a = X.Engine(sub, 4, 1, None, mc_seed=11)
        b = Q.Engine(sub, 4, 1, None, mc_seed=11)
        ra = a._run("x", None, {1.0: 0.1, 2.0: 0.2}, {1.0: 0.0, 2.0: 0.1}, 5)
        rb = b._run("x", None, {1.0: 0.1, 2.0: 0.2}, {1.0: 0.0, 2.0: 0.1}, 5)
    finally:
        gate.run_gate = real
    out = []
    if calls[0] != calls[1]:
        out.append("the two engines passed different arguments to gate.run_gate")
    for arm in ("bound", "point"):
        out += A.rows_same([ra[arm]], [{k: v for k, v in rb[arm].items() if k in ra[arm]}])
        missing = [c for c in Q.EXTRA if c not in rb[arm]]
        if missing:
            out.append(f"{arm}: EXTRA not kept: {missing}")
        if "not_kept" in rb[arm]:
            out.append("a column outside the kept set was kept")
        shift = "lower_bound" if arm == "bound" else "point"
        want = V.path_values(fake_paths(100 + (0 if arm == "bound" else 1)), sub.margin)["required"]
        if not np.array_equal(np.asarray(rb[arm][Q.REQUIRED]), want):
            out.append(f"{arm}: the per-path required bankroll is not the hook's ({shift})")
    for m in ("path_problems",):
        if getattr(Q.Engine, m) is not getattr(VS.Engine, m):
            out.append(f"Q.Engine.{m} is not the vendored method")
    # run(): the vendored labels and cache; every result kept by label
    gate.run_gate = fake_run_gate
    try:
        e = Q.Engine(sub, 4, 1, VS.Resume(None, "check"), mc_seed=1)
        r1 = e.run("registered")
        r2 = e.run("a1 mean_block 5", mean_block=5)
        r3 = e.run("a1 mean_block 5", mean_block=5)
    finally:
        gate.run_gate = real
    if e.labels != ["a1 mean_block 5"] or list(e.results) != ["registered", "a1 mean_block 5"]:
        out.append(f"labels {e.labels}, results {list(e.results)}")
    if r2 != r3 or len(e.seconds) != 2:
        out.append("a cached run was run again")
    if not isinstance(r1["bound"][Q.REQUIRED], list):
        out.append("the required bankroll did not survive the cache's JSON")
    gate.run_gate = fake_run_gate
    try:
        kept, dropped = Q.Engine(sub, 4, 1, None, mc_seed=1), Q.Engine(sub, 4, 1, None, mc_seed=1, keep_sink=False)
        kept.sink.append({"path": 0})
        dropped.sink.append({"path": 0})
        rk, rd = kept.run("a1 mean_block 5", mean_block=5), dropped.run("a1 mean_block 5", mean_block=5)
    finally:
        gate.run_gate = real
    if rk != rd or len(kept.sink) != 1 or dropped.sink:
        out.append("keep_sink=False changed a row or kept the record")
    return out


# ------------------------------------------------------------------------------------------------ ruin


def check_ruin() -> list[str]:
    out = []
    req = [100.0, 200.0, 300.0, 400.0, 1000.0]
    if Q.share_above(req, 300.0) != 0.4 or Q.share_above(req, 1000.0) != 0.0 or Q.share_above(req, 99.0) != 1.0:
        out.append("share_above is not the strict share above")
    if not math.isnan(Q.share_above([], 1.0)) or not math.isnan(Q.share_above(req, float("nan"))):
        out.append("share_above of nothing is not NaN")
    rng = np.random.default_rng(3)
    r = rng.gamma(2.0, 800.0, 500)
    p90 = float(np.percentile(r, 90))
    arm = {"pf_growth_on_base_p50": 0.5, "pf_required_p90": p90, "pf_required_p50": float(np.median(r)),
           "pf_required_p99": float(np.percentile(r, 99)), "pf_required_worst": float(r.max()), "ruin_probability": 0.0,
           "v1_share_below_start": 0.1, Q.REQUIRED: r.tolist()}
    ref = {"pf_required_p90": 1500.0}
    c = Q.ruin_columns(arm, ref)
    if c["share_required_above_own_p90"] != float(np.mean(r > p90)) or not 0.09 <= c["share_required_above_own_p90"] <= 0.11:
        out.append(f"the share above its own p90 {c['share_required_above_own_p90']}")
    if c["share_required_above_reference_p90"] != float(np.mean(r > 1500.0)):
        out.append("the share above the reference's p90")
    for k in ("ruin_probability", "pf_required_worst", "pf_required_p99", "v1_share_below_start", "ruin_form"):
        if k not in c:
            out.append(f"{k} not carried")
    if c["paths_read"] != 500 or "D-312" not in c["ruin_form"]:
        out.append("paths read or the form's label")
    res = {"registered": {"bound": arm, "point": arm}, "a1 mean_block 5": {"bound": arm, "point": {**arm, Q.REQUIRED: []}}}
    rows = Q.ruin_rows(res, {"registered": "registered", "a1 mean_block 5": "registered"},
                       {"bound": "verdict", "point": "point"}, lambda x: "A1", "P14")
    if len(rows) != 4 or rows[2]["reference_run"] != "registered" or rows[3]["paths_read"] != 0 \
            or not math.isnan(rows[3]["share_required_above_own_p90"]):
        out.append("ruin_rows' rows or references")
    return out


# ------------------------------------------------------------------------------------------------ A2


def body(fn) -> str:
    src = inspect.getsource(fn)
    i = src.index("\n    import customer_slices as cs")
    return src[i:]


def check_a2_source() -> list[str]:
    want = body(VS.part_a2)
    for a, b in (("V.SEED_A2", "int(seed)"), ("_cached(", "VS._cached("), ("replay_form(sub)", "VS.replay_form(sub)")):
        if a not in want:
            return [f"the vendored part_a2 no longer holds {a!r} (the adapter's reason is gone)"]
        want = want.replace(a, b)
    got = body(Q.part_a2)
    if got != want:
        import difflib

        return ["Q.part_a2 differs from the vendored part beyond its seed: "
                + " | ".join(list(difflib.unified_diff(want.splitlines(), got.splitlines(), lineterm=""))[2:12])]
    return []


def check_a2_rows() -> list[str]:
    import customer_slices as cs

    from propedge.campaign import lockstep, shared_days

    sub = A.subject("P14", eras=False, flagged=False, seed=5)
    sub = type(sub)(**{**sub.__dict__, "days": [f"d{i:04d}" for i in range(300)]})
    used: list[int] = []

    def path_of(seed: int, n: int):
        rng = np.random.default_rng(seed)
        cash = np.concatenate([[100.0], 100.0 + np.cumsum(rng.normal(0, 10, n))])
        return SimpleNamespace(path=SimpleNamespace(cash_series=cash.tolist(), initial_bankroll=100.0,
                                                    days_to_first_payout=None, payout_gaps=[]))

    class FakeDraws:
        def __init__(self, blocks, seed, mean_block=None, **kw):
            self.seed, self.L = int(seed), mean_block

        def lockstep_kwargs(self):
            return {"_mb": self.L}

    def fake_sim(protocol, seed, horizon_days, _mb=None, **kw):
        used.append(int(seed))
        return path_of(int(seed) + (0 if _mb is None else int(_mb) * 7919), horizon_days - 1)

    def fake_replay(blocks, args, horizon=None):
        return path_of(int(sum(blocks)), len(blocks))

    def fake_form(s):
        blk = list(range(len(s.days)))
        return {"verdict": (blk, {"draws": {"protocol": None}, "path": {}}),
                "point": ([x + 1 for x in blk], {"draws": {"protocol": None}, "path": {}})}

    saved = (lockstep.simulate_lockstep_path, shared_days.SharedDayDraws, cs.replay, VS.replay_form)
    lockstep.simulate_lockstep_path, shared_days.SharedDayDraws, cs.replay, VS.replay_form = (
        fake_sim, FakeDraws, fake_replay, fake_form)
    try:
        a = VS.part_a2(sub, 3, 6, VS.Resume(None, "check"))
        used_a = list(used)
        used.clear()
        b = Q.part_a2(sub, 3, 6, VS.Resume(None, "check"), seed=V.SEED_A2)
        used_b = list(used)
        used.clear()
        c = Q.part_a2(sub, 3, 6, VS.Resume(None, "check"), seed=20261953)
        used_c = list(used)
    finally:
        lockstep.simulate_lockstep_path, shared_days.SharedDayDraws, cs.replay, VS.replay_form = saved
    out = A.rows_same(a, b)
    if used_a != used_b or set(used_a) != set(lockstep.path_seeds(V.SEED_A2, 6)):
        out.append("the vendored seed's paths are not path_seeds(SEED_A2)")
    if set(used_c) != set(lockstep.path_seeds(20261953, 6)) or set(used_c) & set(used_a):
        out.append("another seed did not draw other paths")
    if len(a) != 2 * (1 + len(V.MEAN_BLOCKS)):
        out.append(f"{len(a)} rows, not two arms x {1 + len(V.MEAN_BLOCKS)} schemes")
    real_a = [(r["arm"], r["starts"]) for r in a]
    real_c = [(r["arm"], r["starts"]) for r in c]
    if real_a != real_c or any(r["starts"] != 3 for r in c):
        out.append("the real-order side moved with the seed")
    if Q.a2_path_sets(c) != [f"a2 {r['scheme']} {r['arm']}" for r in c] or len(Q.a2_path_sets(c)) != 10:
        out.append("A2's path sets")
    short = type(sub)(**{**sub.__dict__, "days": sub.days[:100]})
    d = Q.part_a2(short, None, 6, None, seed=20261953)
    if len(d) != 1 or d[0]["computable"] or Q.a2_path_sets(d):
        out.append("a short history is not 'not computable'")
    return out


# ------------------------------------------------------------------------------------------------ D-583's readings


class Eng(A.FakeEngine):
    """Q-18's fake engine with `results`, the kept extras and a per-path required bankroll."""

    def __init__(self, sub):
        super().__init__(sub)
        self.results = {}

    def growth(self, blocks, lb_by):
        if isinstance(blocks, dict) and blocks.get("twin"):
            return 0.9
        return super().growth(blocks, lb_by)

    def run(self, label, *, blocks=None, e_by=None, lb_by=None, mean_block=None):
        res = super().run(label, blocks=blocks, e_by=e_by, lb_by=lb_by, mean_block=mean_block)
        for k, arm in enumerate(("bound", "point")):
            res[arm].update({c: 0.5 + k for c in Q.EXTRA})
            res[arm][Q.REQUIRED] = list(np.linspace(1.0, 20.0, 20) + k)
        self.results[label] = res
        return res


def check_slip_b() -> list[str]:
    sub = A.subject("P14", eras=False, flagged=False)
    sub.extra.update({"lb05_by": {R: v + 0.01 for R, v in sub.lb_by.items()}, "flagged": True})
    reg = Eng(sub).run("registered")
    reg05 = Eng(sub).run("registered at 0.05")
    eng = Eng(sub)

    def rebound(tt):
        e = {R: float(np.nanmean(tt[f"r_{R:g}"])) for R in A.KEYS}
        return e, {R: e[R] - 0.04 for R in A.KEYS}, {R: e[R] - 0.08 for R in A.KEYS}, True

    def zeb(blocks, e_by, frr):
        return {"twin": True, "of": blocks, "n": 0, "e_removed": dict(e_by), "frr": frr}

    sl_calls = []

    def slices(name, blocks, e_by, lb05):
        sl_calls.append((name, blocks, dict(e_by), dict(lb05)))
        lvl = {a["arm"]: a["level"] for a in ps16.arms()}[name]
        hold = lvl <= 3
        lines = [{"line": x, "measure": m, "candidate": 1.0, "reference": 1.0, "holds": hold}
                 for x, m in (("a", "share_positive"), ("b", "net_p10"), ("c", "share_no_payout"),
                              ("d", "needed_bankroll_p95"))]
        return pd.DataFrame([{"config": name, "arm": "verdict", "horizon": 63, "n_slices": 5}]), lines, hold

    res_rows = [{"rr": 1.0, "resolves": True, "unresolved": 0.01}, {"rr": 2.0, "resolves": True, "unresolved": 0.02}]
    rows, srows, refs = Q.part_slip_b(eng, reg, reg05, rebound, slices, lambda tt: res_rows, zeb)
    out = []
    arms = ps16.arms()
    want = []
    for a in arms:
        if a["arm"] != "base":
            want += [f"slip {a['arm']}", f"slip05 {a['arm']}"]
        want.append(f"twin {a['arm']}")
    if eng.labels != want:
        out.append(f"the runs {eng.labels[:6]}..., not {want[:6]}...")
    calls = {c["label"]: c for c in eng.calls}
    for a in arms:
        name = a["arm"]
        tt = sub.t if name == "base" else ps16.stress(sub.t, a)
        e, lb05, lbn, _ = rebound(tt) if name != "base" else (sub.e_by, sub.extra["lb05_by"], sub.lb_by, True)
        blocks = sub.rebuild(tt) if name != "base" else list(sub.blocks)
        if name != "base":
            if calls[f"slip {name}"]["lb_by"] != lbn or calls[f"slip {name}"]["blocks"] != blocks:
                out.append(f"{name}: the verdict-level run is not on its stressed trades at 0.05/N")
            if calls[f"slip05 {name}"]["lb_by"] != lb05 or calls[f"slip05 {name}"]["e_by"] != e:
                out.append(f"{name}: the D-583-level run is not at the 0.05 bound")
        tw = calls[f"twin {name}"]
        if not (isinstance(tw["blocks"], dict) and tw["blocks"].get("twin") and tw["blocks"]["e_removed"] == dict(e)
                and set(tw["e_by"].values()) == {0.0} and set(tw["lb_by"].values()) == {0.0}):
            out.append(f"{name}: the twin is not its trades less its own e at e = bound = 0")
    if [c[0] for c in sl_calls] != [a["arm"] for a in arms]:
        out.append("the slices were not read once an arm")
    for name, _, e, lb05 in sl_calls[1:]:
        tt = ps16.stress(sub.t, next(a for a in arms if a["arm"] == name))
        if lb05 != rebound(tt)[1]:
            out.append(f"{name}: the slices are not at the 0.05 bound")
    sb = [r for r in rows if r["section"] == "slip_b"]
    if len(sb) != 3 * len(arms):
        out.append(f"{len(sb)} slip_b rows, not 3 an arm")
    base_v = [r for r in sb if r["scheme"] == "base" and r["bound_level"] == Q.LEVEL_VERDICT and r["arm"] != "point"]
    if len(base_v) != 1 or base_v[0]["pf_growth_on_base_p50"] != reg["bound"]["pf_growth_on_base_p50"] \
            or base_v[0]["era_flagged"] is not True or base_v[0]["growth_zero_edge_twin"] != 1.0:
        out.append("the base verdict-level row is not the registered run's, with its flag and twin")
    if any(r["share_accounts_ever_paid"] not in (0.5, 1.5) for r in sb):
        out.append("the share ever paid not carried")
    if {r["slice_lines_hold"] for r in sb} != {True, False} or any("slice_d_holds" not in r for r in sb):
        out.append("the slice lines not carried")
    if not all(r["every_offered_r_resolves"] is True and r["resolution_worst_unresolved"] == 0.02 for r in sb):
        out.append("the resolution not carried")
    if refs.get("slip05 A_stop2") != "registered at 0.05" or refs.get("twin B_slip5") != "twin base" \
            or refs.get("slip A_stop2") != "registered":
        out.append(f"the references {refs}")
    if len([r for r in srows if r["section"] == "slip_b_lines"]) != 4 * len(arms):
        out.append("the lines' rows")
    rd = Q.slip_readings(rows, sub.arm_names)
    if len(rd) != 4:
        out.append(f"{len(rd)} reading rows, not two families at two levels")
    for r in rd:
        lv = r["bound_level"]
        fam_rows = sorted([x for x in sb if x["bound_level"] == lv and x["arm"] != "point"
                           and x["family"] in ("base", r["family"])], key=lambda x: x["level"])
        exp_low = next((x["level"] for x in fam_rows if not x["pf_growth_on_base_p50"] > 0), ps16.NONE)
        exp_high = max((x["level"] for x in fam_rows if x["slice_lines_hold"]), default=ps16.NONE)
        if r["lowest_level_growth_at_bound_at_or_below_zero"] != exp_low or \
                r["highest_level_all_slice_lines_hold"] != exp_high:
            out.append(f"{lv} family {r['family']}: the reading {r} is not ({exp_low}, {exp_high})")
    if all(r["lowest_level_growth_at_bound_at_or_below_zero"] == ps16.NONE for r in rd):
        out.append("no family turned: the synthetic case does not exercise the reading")
    if {r["highest_level_all_slice_lines_hold"] for r in rd} != {3}:
        out.append("the slice-line reading is not the highest level holding them")
    bad = sub.t.copy()
    bad.loc[bad.index[0], "o_1"] = "x"
    try:
        import dataclasses

        Q.part_slip_b(Eng(dataclasses.replace(sub, t=bad)), reg, reg05, rebound, slices, lambda tt: res_rows, zeb)
        out.append("an unknown exit kind was not refused")
    except (ValueError, SystemExit):
        pass
    return out


# ------------------------------------------------------------------------------------------------ slices


def summary(config: str, shift: float = 0.0) -> list[dict]:
    import customer_slices as cs

    rows = []
    for h in (21, 63, 126):
        r = {"section": "slices", "config": config, "arm": "verdict", "horizon": float(h)}
        r.update({c: float(i) + h / 100.0 + shift for i, c in enumerate(cs.SUMMARY_COLS)})
        rows.append(r)
    return rows


def check_slices() -> list[str]:
    import a3_brk30_cb20 as C
    import customer_slices as cs

    out = []
    reg = pd.DataFrame(summary(C.CANDIDATE_SLICE) + summary("fv3c", 0.001)
                       + [{"section": "gate", "config": None, "arm": None, "horizon": None}])
    cand = Q.summary_frame(reg[reg["section"] == "slices"], C.CANDIDATE_SLICE)
    fv = Q.summary_frame(reg[reg["section"] == "slices"], "fv3c")
    if list(cand["horizon"]) != [21, 63, 126] or len(fv) != 3:
        out.append("summary_frame's pick")
    mine = pd.DataFrame(summary(C.CANDIDATE_SLICE))
    mine["horizon"] = mine["horizon"].astype(int)
    if Q.summary_problems(mine, cand, cs.SUMMARY_COLS, C._slice_same):
        out.append("equal summaries flagged")
    worse = mine.copy()
    worse.loc[1, "net_p10"] += 1e-6
    if not Q.summary_problems(worse, cand, cs.SUMMARY_COLS, C._slice_same):
        out.append("a changed summary not caught")
    lines, hold = Q.slice_lines_of(mine, fv, C.CANDIDATE_SLICE, C.slice_lines)
    exp = C.slice_lines(pd.concat([mine, fv], ignore_index=True), candidate=C.CANDIDATE_SLICE, reference="fv3c")
    if lines != exp or hold != all(r["holds"] for r in exp) or len(lines) != 4:
        out.append("slice_lines_of is not a3_brk30_cb20.slice_lines on the two summaries")
    reg_lines = pd.DataFrame([{**r, "holds": str(r["holds"])} for r in exp])
    if Q.lines_problems(lines, reg_lines, C._slice_same):
        out.append("equal lines flagged")
    flip = [{**r, "holds": (not r["holds"]) if r["line"] == "c" else r["holds"]} for r in lines]
    if not Q.lines_problems(flip, reg_lines, C._slice_same):
        out.append("a changed line not caught")
    sub = A.subject("P14", eras=False, flagged=False)
    sub = type(sub)(**{**sub.__dict__, "kw": {"n_paths": 500, "purchase_budget": (20, 21), "e": 9.0, "lb": 9.0,
                                              "seed": 1, "one_at_a_time": None, "risk_policy": "nc", "rtp": False}})
    camp = Q.slice_campaign(sub, "x", [1, 2], {1.0: 0.1, 2.0: 0.2}, {1.0: -0.1, 2.0: -0.3}, seed=20261028,
                            strict_gap=5.0)
    kw = camp.kw
    if "n_paths" in kw or "purchase_budget" in kw or kw["e"] != 0.2 or kw["lb"] != -0.3 or kw["seed"] != 20261028 \
            or kw["one_at_a_time"] != 5.0 or kw["lb_by_rr"] != {1.0: -0.1, 2.0: -0.3} or kw["rtp"] is not False:
        out.append(f"slice_campaign's engine arguments {kw}")
    if camp.dates != [str(d) for d in sub.days] or camp.blocks != [1, 2]:
        out.append("slice_campaign's days or blocks")
    return out


# ------------------------------------------------------------------------------------------------ the file


def check_file_identity() -> list[str]:
    from extended.results import write_result

    rows = [{"section": "a1", "arm": "verdict", "x": 1.0 / 3.0, "y": float("inf"), "flag": True, "n": 500,
             "note": "a, b", "blank": float("nan")},
            {"section": "a1", "arm": "point", "x": 2.0 / 3.0, "y": -1e-17, "flag": False, "n": 3, "note": "none",
             "blank": None},
            {"section": "slip_reading", "lowest": "none", "x": 0.1 + 0.2},
            {"section": "slip_reading", "lowest": 5, "x": 1e300}]
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        csv, _ = write_result(pd.DataFrame(rows), "q18b_check", script="tests/p14_validation_b_checks.py", seed=1,
                              parameters={}, results_dir=Path(tmp), exploratory=True)
        old = Q.read_file(csv)
        bad = Q.file_problems(rows, old, ("a1", "slip_reading"))
        if bad:
            out.append(f"equal rows flagged: {bad[:3]}")
        for k, v in (("x", np.nextafter(1.0 / 3.0, 1.0)), ("flag", False), ("blank", 0.0), ("note", "a,b"),
                     ("n", 501)):
            changed = [dict(r) for r in rows]
            changed[0][k] = v
            if not Q.file_problems(changed, old, ("a1",)):
                out.append(f"a changed {k} not caught")
        extra = [dict(r) for r in rows]
        extra[1]["new_col"] = 1.0
        if not Q.file_problems(extra, old, ("a1",)):
            out.append("a value in a column the file lacks not caught")
        if not Q.file_problems(rows[:1], old, ("a1",)):
            out.append("a missing row not caught")
    ref = {"bound": pd.Series({"ruin_probability": 0.0, "share_accounts_ever_paid": 0.25}),
           "point": pd.Series({"ruin_probability": 0.0, "share_accounts_ever_paid": float("nan")})}
    good = {"bound": {"ruin_probability": 0.0, "share_accounts_ever_paid": 0.25}, "point": {"ruin_probability": 0.0}}
    if Q.registered_extra_problems(good, ref):
        out.append("equal extras flagged")
    if not Q.registered_extra_problems({**good, "bound": {**good["bound"], "share_accounts_ever_paid": 0.2500001}}, ref):
        out.append("a changed extra not caught")
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "r.jsonl"
        p.write_text('{"_label": "a", "row": 1}\n{"_label": "b", "row": 2}\n', encoding="utf-8")
        m = json.loads(Q.file_manifest(p, commit="abc").read_text(encoding="utf-8"))
        import hashlib

        if m["sha256"] != hashlib.sha256(p.read_bytes()).hexdigest() or m["lines"] != 2 or m["commit"] != "abc":
            out.append(f"the resume manifest {m}")
    return out


# ------------------------------------------------------------------------------------------------ assumptions


def check_assumptions() -> list[str]:
    sub = A.subject("P14", eras=False, flagged=False)
    proto = SimpleNamespace(payout_path="standard", payout_frac=1.0, keep_balance=0.0)
    sub = type(sub)(**{**sub.__dict__, "kw": {"levels": (0.0,), "rtp": False, "purchase_budget": (20, 21),
                                              "one_at_a_time": 5.0, "bankroll": 1e8, "protocol": proto,
                                              "rules": SimpleNamespace(subscription=49.0)}})
    rows = Q.assumption_rows(sub, payout_lag_days=3, payout_method="aeropay", fills_profile="assumed",
                             base_ticks={"entry": 1, "stop": 1}, plan_id="noclose")
    by = {r["assumption"]: r for r in rows}
    out = []
    want = {"payout_denial": [0.0], "placement": False, "focused_trader": False, "purchase_budget": [20, 21],
            "strict_rule_minutes": 5.0, "state_table": "noclose", "bankroll": 1e8}
    for k, v in want.items():
        if k not in by or json.loads(by[k]["value"]) != v:
            out.append(f"{k}: {by.get(k, {}).get('value')!r}, not {v!r}")
    for k in ("fills", "payout_model", "breakeven_move"):
        if k not in by:
            out.append(f"{k} not stated")
    pm = json.loads(by["payout_model"]["value"])
    if pm["payout_lag_days"] != 3 or pm["payout_method"] != "aeropay" or pm["subscription"] != 49.0:
        out.append(f"the payout model {pm}")
    if any(not r["source"] or not r["meaning"] for r in rows):
        out.append("an assumption without its source or meaning")
    sub2 = type(sub)(**{**sub.__dict__, "kw": {**sub.kw, "focused_trader": object()}})
    if json.loads({r["assumption"]: r for r in Q.assumption_rows(
            sub2, payout_lag_days=3, payout_method="aeropay", fills_profile="assumed", base_ticks={},
            plan_id=None)}["focused_trader"]["value"]) is not True:
        out.append("a Focused Trader in the call is not reported on")
    return out


# ------------------------------------------------------------------------------------------------ the runner


def check_runner() -> list[str]:
    m = _load("p14_validation_b", "scripts/p14_validation_b.py")
    out = []
    labels = ["registered at 0.05", "twin base", "slip A_stop2", "slip05 A_stop2", "twin A_stop2", "a1 mean_block 5",
              "b2 independent step 1", "c1 drop10 realisation 0"]
    if [m.part_of(x) for x in labels] != ["identity", "SLIPB", "SLIP", "SLIPB", "SLIPB", "A1", "B2", "C1"]:
        out.append(f"part_of {[m.part_of(x) for x in labels]}")
    if [m.reference_of(x) for x in labels] != ["registered at 0.05", "twin base", "registered", "registered at 0.05",
                                               "twin base", "registered", "registered", "registered"]:
        out.append(f"reference_of {[m.reference_of(x) for x in labels]}")
    if m.new_runs(labels, ["a2 independent verdict"]) != ["slip05 A_stop2", "twin A_stop2", "a2 independent verdict"]:
        out.append(f"new_runs {m.new_runs(labels, ['a2 independent verdict'])}")
    if m.remade_runs(labels) != ["slip A_stop2", "a1 mean_block 5", "b2 independent step 1", "c1 drop10 realisation 0"]:
        out.append(f"remade_runs {m.remade_runs(labels)}")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "variants.jsonl").write_text("\n".join(json.dumps(x) for x in (
            {"prereg_id": "Q-18:p14_validation", "params": {"run": "a1 mean_block 1"}},
            {"prereg_id": "other", "params": {"run": "a1 mean_block 5"}},
            {"prereg_id": "Q-18:p14_validation", "params": {"run": "slip A_stop2"}})) + "\n", encoding="utf-8")
        if m.old_variant_runs(Path(tmp)) != ["a1 mean_block 1", "slip A_stop2"]:
            out.append("old_variant_runs")
    ref = pd.Series({c: 1.0 for c in VS.IDENT_COLS + ("ruin_probability",)})
    if m.twin_problems({"point": {c: 1.0 for c in VS.IDENT_COLS + ("ruin_probability",)}}, ref):
        out.append("an equal twin flagged")
    if not m.twin_problems({"point": {**{c: 1.0 for c in VS.IDENT_COLS}, "ruin_probability": 0.5}}, ref):
        out.append("a changed twin not caught")
    st = m.git_state()
    line = m.provenance_line(st, ["--check"])
    if not st["commit"] or st["commit"] not in line or "--check" not in line:
        out.append(f"the provenance line {line}")
    if m.SEED_A2 != 20261953 or m.SEED_A2 in {m.P.SEED_B1, m.P.SEED_C1, m.P.SEED_MC, m.P.P14_CAMPAIGN_SEED}:
        out.append("SEED_A2")
    if m.P.SCRIPT != "scripts/p14_validation.py" or m.RESULT == m.P.RESULT:
        out.append("the runner would write the existing file")
    for argv in ([], ["--part", "A2"], ["--check", "--workers", "3"], ["--check", "--part", "B1"]):
        try:
            code = m.main(argv)
        except SystemExit as e:
            code = e.code
        if code != 2:
            out.append(f"{argv}: exit {code}, not 2")
    return out


CHECKS = {"engine_run": check_engine_run, "ruin": check_ruin, "a2_source": check_a2_source, "a2_rows": check_a2_rows,
          "slip_b": check_slip_b, "slices": check_slices, "file_identity": check_file_identity,
          "assumptions": check_assumptions, "runner": check_runner}


def main() -> int:
    code = 0
    for name, fn in CHECKS.items():
        try:
            bad = fn()
        except Exception as e:                     # noqa: BLE001 -- a check that raises fails, with its reason
            import traceback

            bad = [f"raised {type(e).__name__}: {e} -- " + traceback.format_exc()[-1500:]]
        if bad:
            code = 3
            print(f"FAILS: {name} -- " + "; ".join(bad[:6]), flush=True)
        else:
            print(f"HOLDS: {name}", flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
