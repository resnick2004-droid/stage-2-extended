"""Wave 5's survey runner (`extended/survey.py`), build v3, end to end on the synthetic worlds of
`tests/survey_world.py`: Wave 3.4's engine with Q-192, Q-192b and rm3-b (wt/wt-features 3452952), W42-R1 as it
stands (c014d0a: its module and public scoring functions, its application script, its real output file made by
`wave42_apply.apply`), Q-197's calendar loader (master 990d874). No bar, no result file of the repository, no held-out
calendar: every input and output is in a temporary folder (`SV.ROOT` pointed there).

* W42-R1's public functions reproduce its own `setting_rule` outputs on its H4 reading (the identity);
* the planted region is found within budget; in every other world there is no finalist, each world checked to bite;
* every cell is counted (through Q-192's pens), the bytes repeat, one ledger a run;
* the refusals (pins, rows, bindings, data, the space's digest, the allowlist, the spec's form, held-out first, the
  calendar, the runner's values, a second run, the engine, W42-R1's public functions, an unset limit, the process
  under a pin);
* M-2's do-nothing floor at 10, 11, 25 and 43 seeds;
* a mutation of each step is killed by its scenario's own verdict, an exception counting only when it is the expected
  refusal.
"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import ROOT as REPO
from extended import reader as R

import survey_world as W   # noqa: E402  (tests/ is on sys.path under pytest's rootdir)

W42, APPLY = W.load_w42()
from extended import survey as SV  # noqa: E402

RARE_Q = -8.0       # payouts rare: almost no unit passes by W, so B-5 puts every cost z at 0


@pytest.fixture(scope="module")
def eng():
    E = SV.Engine.default()
    E.check()
    return E


@pytest.fixture(scope="module")
def roots(tmp_path_factory):
    out = {}
    for tag, spread, base in (("default", 0.0, 0.0), ("wide", 0.2, 0.0), ("rare", 0.0, RARE_Q)):
        root = tmp_path_factory.mktemp(f"root_{tag}")
        out[tag] = dict(W.w42_root(root, spread, base), root=root)
    return out


@contextlib.contextmanager
def at(root: Path):
    old = SV.ROOT
    SV.ROOT = root
    try:
        yield
    finally:
        SV.ROOT = old


ORDER: list[str] = []


def local_writer(df, name, *, script, seed, parameters, results_dir, **kw):
    d = Path(results_dir)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{name}.csv"
    if p.exists():
        raise FileExistsError(p)
    p.write_bytes(df.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    m = d / f"{name}.csv.manifest.json"
    m.write_text(json.dumps({"script": script, "seed": seed, "parameters": parameters, **kw}, sort_keys=True,
                            default=str), encoding="utf-8")
    ORDER.append(name)
    return p, m


def local_variants(rows, results_dir):
    p = Path(results_dir) / "variants.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
    ORDER.append("variants")
    return p


def protocol_sha(eng, spec_over=None) -> str:
    pr = dict(W.SPEC["protocol"], **((spec_over or {}).get("protocol", {})))
    fi = dict(W.SPEC["finalists"], **((spec_over or {}).get("finalists", {})))
    p = eng.SS.Protocol(pr["measure"], tuple(tuple(b) for b in pr["blocks"]), tuple(pr["seeds"]), pr["horizon"])
    return eng.SS.protocol_sha256(p, tuple(fi["reread_seeds"]), tuple(lim.name for lim in W42.LIMITS))


def declare(eng, tmp: Path, kind="plateau", *, spec_over=None, parts=None, values_row="fixture", **part_kw) -> Path:
    block = SV.declare_parts(parts or W.parts_of(kind, **part_kw), eng)
    try:
        psha = protocol_sha(eng, spec_over)
    except eng.SS.HeldOutInput:                     # a held-out protocol: the survey itself must refuse it
        psha = "0" * 64
    s = W.spec(block, protocol_sha256=psha, code_sha256=SV.objective_code_sha(),
               values_row=values_row, **(spec_over or {}))
    (tmp / "decl").mkdir(parents=True, exist_ok=True)
    decl = tmp / "decl" / "F-99_decl.md"
    decl.write_bytes(W.declaration(s).encode("utf-8"))
    return decl


def run(eng, root: Path, decl: Path, out: Path, **kw):
    W.CALLS.clear()
    kw.setdefault("engine", eng)
    kw.setdefault("writer", local_writer)
    kw.setdefault("variants_writer", local_variants)
    with at(root):
        return SV.run_survey(decl, results_dir=out, name="F-99_survey", pin_fixture=SV.fixture_pin(decl), **kw)


def survey(eng, tmp: Path, roots, kind="plateau", root="default", **kw):
    return run(eng, roots[root]["root"], declare(eng, tmp, kind, **kw), tmp / "out")


def rows_of(p: Path) -> list[dict]:
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]


def csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p, dtype=str, keep_default_na=False)


def audit(out, spec=W.SPEC) -> list[str]:
    """Re-derived from the outputs: what a correct survey holds whatever its world."""
    probs = []
    led = out.ledger
    if led.roles.get("survey", {}).get("seed") != spec["survey"]["seed"]:
        probs.append("the survey's role seed is not the declared one")
    if sum(r["role"] == "survey" and r["status"] == "proposed" for r in led.rows) != spec["survey"]["n"]:
        probs.append("the survey is not the declared size")
    for i in range(1, spec["rounds"]["count"] + 1):
        rr = [r for r in led.rows if r["role"] == f"round-{i}"]
        if led.roles.get(f"round-{i}", {}).get("seed") != spec["rounds"]["seed"] or len(rr) != spec["rounds"]["batch"]:
            probs.append(f"round {i} is not the declared batch under the declared seed")
    if f"round-{spec['rounds']['count'] + 1}" in led.roles:
        probs.append("a round past the declared count")
    cells = {r["id"] for r in led.rows if r["status"] == "proposed"}
    if not set(W.CALLS) <= cells:
        probs.append("the runner ran a design that is not a counted cell")
    if len(rows_of(out.variants_path)) != len(led.rows):
        probs.append("the variants rows are not the ledger's cells")
    if R.sha256_lf(out.list_path) != out.list_sha256:
        probs.append("the list sha is not the list file's")
    lst, reads = csv(out.list_path), csv(out.readings_path)
    rr = {r["id"]: float(r["value"]) for _, r in reads.iterrows()
          if r["role"] == "reread" and r["measure"] == "composite"}
    for _, f in lst.iterrows():
        if abs(float(f["reread_value"]) - rr.get(f["id"], float("nan"))) > 1e-12:
            probs.append(f"finalist {f['id']}'s reread value is not its re-read reading")
    if out.finalists:
        m = R.HELDOUT_TOKENS["finalists"].match(f"| E-999 | 2026-11-20 | {out.token} -- the finalists |")
        if not m or m.group("sha") != out.declaration_sha256 or m.group("list") != out.list_sha256 \
                or m.group("decl") != spec["prereg_id"]:
            probs.append("the token is not Q-158's form for this declaration and list")
        vals = [float(x) for x in lst["selection_value"]]
        if vals != sorted(vals):
            probs.append("the finalists are not in the declared order")
        for f in out.finalists:
            if set(f["gaps"]) != set(SV.BASELINES) or not all(g["t"] > g["threshold"] for g in f["gaps"].values()):
                probs.append(f"finalist {f['id']} does not beat each baseline")
            if not all(v["inside"] for v in f["limits"].values()) or not f["no_harm"]["held"] or \
                    not f["do_nothing"]["held"] or not f["plateau"]["accepted"]:
                probs.append(f"finalist {f['id']} is outside a limit or a floor, or not on a plateau")
    elif out.token is not None or len(lst):
        probs.append("no finalist, but a token or a list row")
    if len(lst) != len(out.finalists) or len(csv(out.candidates_path)) != len(out.candidates) + len(out.floored):
        probs.append("the list or the candidates file does not hold the run's")
    return probs


def in_region(design) -> bool:
    return W.bump(design) >= 0.5 * W.A


def hot(design) -> bool:
    return W.bump(design) >= 0.1 * W.A


def reasons(out) -> str:
    return " | ".join(str(c.get("reason", "")) for c in out.candidates + out.floored)


# ------------------------------------------------------------------------------------------------ the scenarios
# Each returns True when the survey behaves correctly in its world, and checks that the world bites.


def sc_planted(eng, tmp, roots):
    out = survey(eng, tmp, roots, "plateau")
    return bool(out.finalists) and all(in_region(f["design"]) for f in out.finalists) and audit(out) == []


def _none(kind, bite, root="default", spec_over=None, **runner):
    def sc(eng, tmp, roots):
        params = dict(runner, kind=kind)
        if "harm" in params:
            params.update(harm=params["harm"] * W.NO_HARM_MARGIN,
                          steady_weight=roots[root]["values"]["weights"]["steady"])
        out = survey(eng, tmp, roots, kind, root=root, runner=params, spec_over=spec_over)
        return out.finalists == [] and audit(out) == [] and bite(out, roots[root])
    return sc


def _spike_bites(out, r):
    return any("plateau" in c for c in out.candidates if abs(c["design"]["x"] - 0.3) < 1e-9)


def _near_bites(out, r):  # a candidate past delta* on every gap and past the t threshold without delta*, not with it
    d = r["values"]["delta_star"]["value"]
    return any(c.get("gaps") and all(g["gap"] > d and g["gap"] / g["se"] > g["threshold"] for g in c["gaps"].values())
               for c in out.candidates)


def _near6_bites(out, r):  # a candidate past the normal z on every gap, short of t(5)'s threshold on one
    return any(c.get("gaps") and 3.0 < min(g["t"] for g in c["gaps"].values()) < c["gaps"]["p16"]["threshold"]
               for c in out.candidates)


def _strong_bites(out, r):
    return any(c.get("gaps") and c["gaps"]["naive_coin"]["beaten"] and not c["gaps"]["p16"]["beaten"]
               for c in out.candidates)


def _limit_bites(name, selection_inside=False):
    def bite(out, r):
        hit = [c for c in out.candidates if c.get("limits") and not c["limits"][name]["inside"]
               and all(g["beaten"] for g in c["gaps"].values())]
        return bool(hit) and (not selection_inside or any(
            c["limits"][name]["selection_value"] >= c["limits"][name]["bound"] for c in hit))
    return bite


def _refused_rows(cls):
    def bite(out, r):
        return any(x.startswith(cls) for x in csv(out.readings_path)["refused"])
    return bite


def _floored_only(floor_name):
    def bite(out, r):
        fl = [f for f in out.floored if hot(f["design"])]
        return bool(fl) and all(floor_name in f["reason"] for f in fl) and \
            not any(hot(c["design"]) for c in out.candidates)
    return bite


def sc_harm_small(eng, tmp, roots):
    """The as-traded side worse by half the margin: inside the floor, so the planted finalists stand."""
    out = survey(eng, tmp, roots, "harm", runner={"kind": "harm", "harm": 0.5 * W.NO_HARM_MARGIN,
                                                  "steady_weight": roots["default"]["values"]["weights"]["steady"]})
    return bool(out.finalists) and all(-W.NO_HARM_MARGIN < f["no_harm"]["as_traded_minus_reflected"] < 0
                                       for f in out.finalists) and audit(out) == []


def sc_censor(eng, tmp, roots):
    """A limit over its own complete starts (W42-R1's horizon): zeros on the starts incomplete over W do not count, so
    the planted finalists stand."""
    out = survey(eng, tmp, roots, "censor")
    return bool(out.finalists) and all(in_region(f["design"]) for f in out.finalists) and audit(out) == []


def sc_mixed(eng, tmp, roots):
    """V-4's order: designs failing the no-harm floor outrank the good ones; floored first, the good ones are ranked."""
    out = survey(eng, tmp, roots, "mixed", runner={"kind": "mixed", "harm": 1.5 * W.NO_HARM_MARGIN,
                                                   "steady_weight": roots["default"]["values"]["weights"]["steady"]})
    harmed = [f for f in out.floored if "no-harm" in f["reason"]]
    best = min((f["selection_value"] for f in out.finalists), default=None)
    return bool(out.finalists) and all(f["design"]["k"] == "a" for f in out.finalists) and \
        best is not None and any(h["selection_value"] < best for h in harmed) and audit(out) == []


def sc_nothing(eng, tmp, roots):
    """V-4 and C-1: with rare payouts W42-R1's do-nothing journey outranks a baseline; a region running it is floored
    before ranking and never a finalist."""
    r = roots["rare"]
    floor = r["values"]["null_journeys"]["floor"]["value"]
    outranks = floor > min(r["values"]["composite"]["value"].values())
    out = survey(eng, tmp, roots, "nothing", root="rare",
                 runner={"kind": "nothing", "base_q": RARE_Q, "fee_unit": r["values"]["budgets"]["fee_unit"]})
    fl = [f for f in out.floored if hot(f["design"])]
    return outranks and out.finalists == [] and bool(fl) and audit(out) == [] and \
        not any(hot(c["design"]) for c in out.candidates)


def meagre_values(r) -> dict:
    """A paid, cheap, poor journey on the rare fixture: composite between every baseline's and the do-nothing floor."""
    v = r["values"]
    caps = {d["name"]: (d["lo"], d["hi"]) for d in v["dimensions"]}
    lo_s, hi_s = caps["speed"]
    lo_b, hi_b = caps["bankroll"]
    lo_c, hi_c = caps["cost"]
    base = W.nothing_values((0,), 1, v["budgets"]["fee_unit"])
    m = {k: float(x[0, 0]) for k, x in base.items()}
    m.update(first_pass_days=10.0, first_payout_days=lo_s + 0.55 * (hi_s - lo_s),
             peak_oop_12_months=lo_b + 0.6 * (hi_b - lo_b), cash_to_first_pass=hi_c, spent_before_first_payout=0.0,
             orders_max=1.0, accounts_max=1.0, taken_mean=10.0)
    return m


def sc_meagre(eng, tmp, roots):
    """M-5: a region failing only the do-nothing floor (paid, so `not_paid_within_B` inside): floored before ranking
    for that floor alone, never a candidate or a finalist."""
    r = roots["rare"]
    out = survey(eng, tmp, roots, "meagre", root="rare",
                 runner={"kind": "meagre", "base_q": RARE_Q, "meagre": meagre_values(r)})
    return out.finalists == [] and audit(out) == [] and _floored_only("the do-nothing floor")(out, r) and \
        all(f["not_paid"]["held"] and f["no_harm"]["held"] for f in out.floored if hot(f["design"]))


def sc_unpaid(eng, tmp, roots):
    """M-5: a region good on the composite but never paid: floored before ranking for `not_paid_within_B` alone."""
    out = survey(eng, tmp, roots, "unpaid")
    return audit(out) == [] and _floored_only("not_paid_within_B")(out, roots["default"]) and \
        all(f["do_nothing"]["held"] and f["no_harm"]["held"] for f in out.floored if hot(f["design"]))


def _refusal(kind, cls, word, **runner):
    def sc(eng, tmp, roots):
        try:
            survey(eng, tmp, roots, kind, runner=dict(runner, kind=kind))
        except cls as e:
            return word in str(e)
        return False
    return sc


def sc_heldout_gated(eng, tmp, roots):
    """F-4: the gated designs' runs labelled held-out -- the whole run refuses at the first, before the gate."""
    try:
        survey(eng, tmp, roots, "gated", runner={"kind": "gated", "hot_tag": "heldout_2024"})
    except eng.SS.HeldOutInput:
        out = tmp / "out"
        return (out / "F-99_survey_failure.csv").is_file() and (out / "variants.jsonl").is_file() and \
            not (out / "F-99_survey_readings.csv").exists()
    return False


def sc_engine_swap(eng, tmp, roots):
    """An engine whose plateau module differs from the bound one refuses, even under a fixture pin."""
    import importlib.util
    src = Path(eng.PL.__file__).read_text(encoding="utf-8") + "\n# a changed engine\n"
    p = tmp / "eng" / "plateau_changed.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("extended.plateau_changed", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["extended.plateau_changed"] = mod
    spec.loader.exec_module(mod)
    try:
        try:
            run(eng, roots["default"]["root"], declare(eng, tmp), tmp / "out", engine=SV.Engine(eng.SS, eng.P, mod))
        except SV.PartRefused as e:
            return "engine" in str(e)
        return False
    finally:
        sys.modules.pop("extended.plateau_changed", None)


def sc_identity(eng, tmp, roots):
    """The public composite and limit estimate are W42-R1's: on its own H4 reading they give `setting_rule`'s baseline
    composites and limit estimates, and the do-nothing floor on W42-R1's null journey (C-1)."""
    ok = True
    for tag in ("default", "rare"):
        r = roots[tag]
        v, sl = r["values"], r["sl"]
        for b in SV.BASELINES:
            c = float(np.mean(W42.composite_per_seed(v, sl, r["readings"][b])))
            ok = ok and abs(c - v["composite"]["value"][b]) < 1e-12
            for lim in v["limits"]["values"]:
                e = W42.limit_estimate(v, sl, r["readings"][b], lim["name"])
                ok = ok and abs(e - lim["baseline_values"][b]) < 1e-12
        with at(r["root"]):
            ob = SV.load_objective(W42)
        ok = ok and abs(ob.floor - v["null_journeys"]["floor"]["value"]) < 1e-15
    return ok


def sc_crossing(eng, tmp, roots):
    """The one-sided check beside a limit: a small excess within the t critical value is not shown; a large one is."""
    return SV.crossing_check(0.5, 1.0, 0.05, 32)[1] is False and SV.crossing_check(3.0, 1.0, 0.05, 32)[1] is True


def sc_do_nothing_exact(eng, tmp, roots):
    """M-2: a design scoring the floor (or one ulp over it) on every seed is refused at 10, 11, 25 and 43 seeds -- the
    counts at which a float mean rounds above it; one past the floor by twice the epsilon is kept."""
    ctx = type("C", (), {})()
    ctx.W = W42                                          # the epsilon is W42-R1's DO_NOTHING_EPS
    with at(roots["default"]["root"]):
        ctx.obj = SV.load_objective(W42)
    f = ctx.obj.floor
    ok = True
    for n in (10, 11, 25, 43):
        for c in (f, float(np.nextafter(f, 2.0))):
            r = type("Rd", (), {"per_seed": (-c,) * n, "value": float(np.mean(np.full(n, -c)))})()
            ok = ok and SV.do_nothing_floor(ctx, r)[0] is False
        good = type("Rd", (), {"per_seed": (-(f + 2e-9),) * n, "value": -(f + 2e-9)})()
        ok = ok and SV.do_nothing_floor(ctx, good)[0] is True
    return ok


def sc_b5(eng, tmp, roots):
    """C-1's self-check: the survey loads only when the public composite of the do-nothing journey is W42-R1's floor."""
    with at(roots["default"]["root"]):
        return SV.load_objective(W42).floor == roots["default"]["values"]["null_journeys"]["floor"]["value"]


SCENARIOS = {
    "planted": sc_planted,
    "noise": _none("noise", lambda out, r: any(c.get("limits") and all(v["inside"] for v in c["limits"].values())
                                               and c["no_harm"]["held"] and c["do_nothing"]["held"]
                                               and not all(g["beaten"] for g in c["gaps"].values())
                                               for c in out.candidates), shift=0.25),
    "spike": _none("spike", _spike_bites),
    "near": _none("near", _near_bites, root="wide"),
    "near6": _none("near", _near6_bites, root="wide", a_near=W.A_NEAR6,
                   spec_over={"finalists": dict(W.SPEC["finalists"], reread_seeds=list(range(201, 207)))}),
    "strong": _none("strong", _strong_bites),
    "ceiling": _none("ceiling", _limit_bites("accounts_max_p90")),
    "floor": _none("floor", _limit_bites("taken_mean_p10")),
    "risky": _none("risky", _limit_bites("taken_mean_p10", selection_inside=True)),
    "tail": _none("tail", _limit_bites("accounts_max_p90")),
    "censor": sc_censor,
    "harm_mid": _none("harm", lambda out, r: "no-harm" in reasons(out), harm=1.5),
    "harm_small": sc_harm_small,
    "coin_side": _none("coin_side", lambda out, r: "no-harm" in reasons(out)),
    "hedge": _none("hedge", _refused_rows("tier1")),
    "overlap": _none("overlap", _refused_rows("overlap")),
    "gated": _none("gated", _refused_rows("gate")),
    "unpaired": _refusal("unpaired", SV.SurveyRefused, "paired"),
    "realkeys": _refusal("realkeys", SV.SurveyRefused, "real path"),
    "range": _refusal("range", SV.SurveyRefused, "outside W42-R1's range"),
    "data": _refusal("data", SV.SurveyRefused, "does not bind"),
    "offcal": _refusal("offcal", SV.SurveyRefused, "calendar"),
    "heldout": sc_heldout_gated,
    "engine_swap": sc_engine_swap,
    "identity": sc_identity,
    "crossing": sc_crossing,
    "nothing": sc_nothing,
    "meagre": sc_meagre,
    "unpaid": sc_unpaid,
    "mixed": sc_mixed,
    "do_nothing_exact": sc_do_nothing_exact,
    "b5": sc_b5,
}


def test_every_scenario_behaves_unmutated(eng, tmp_path, roots):
    """The kill tests' control: each world, unmutated, gives the correct verdict and bites."""
    bad = [name for name, sc in SCENARIOS.items() if not sc(eng, tmp_path / name, roots)]
    assert bad == []


# ------------------------------------------------------------------------------------------------ the mutations


def _with(ctx, **kw):
    c = copy.copy(ctx)
    sp = {k: v for k, v in kw.items() if k in {f.name for f in dataclasses.fields(ctx.spec)}}
    ob = {k: v for k, v in kw.items() if k not in sp}
    if sp:
        c.spec = dataclasses.replace(c.spec, **sp)
    if ob:
        c.obj = dataclasses.replace(c.obj, **ob)
    return c


def _fixed_schedule(orig):
    def m(ctx, d, p, role):
        b = ctx.build_schedule
        ctx.build_schedule = lambda _d: b({"x": 0.0, "y": 0, "k": "a"})
        try:
            return orig(ctx, d, p, role)
        finally:
            ctx.build_schedule = b
    return m


def _reread_from_selection(orig):
    def m(ctx):
        out = orig(ctx)
        for r in ctx.records:
            if "reread_value" in r:
                r["reread_value"] = r["selection_value"]
        return out
    return m


def _overlap_admitted(orig):
    def m(out):
        from extended import components as C
        for path, ps in sorted(out.positions.items()):
            try:
                C.UserBook().extend(ps)
            except C.TierOneRefused as e:
                raise SV._Refused("tier1", str(e)) from e
            except C.OverlapRefused:
                pass
    return m


def _floors_without(name):
    def make(orig):
        def m(ctx, got):
            ok, first, info = orig(ctx, got)
            if first == name:
                rest = [n for n, (o, _) in (("the no-harm floor", SV.no_harm(ctx, got["out"], got["sl"])),
                                            ("the not_paid_within_B limit", SV.not_paid_floor(ctx, got)),
                                            ("the do-nothing floor", SV.do_nothing_floor(ctx, got[ctx.spec.measure])))
                        if not o and n != name]
                return (not rest), (rest[0] if rest else ""), info
            return ok, first, info
        return m
    return make


def _limit_as_mean(orig):
    def m(ctx, arm, sl, lim):
        Wm = ctx.W
        L = next(x for x in Wm.LIMITS if x.name == lim["name"])
        per = {k: np.asarray(v, float) for k, v in arm.items()}
        per.update(Wm.bankroll_states(per, ctx.obj.values["budgets"]["primary"]))
        x = per[L.key][Wm._rows(np.asarray(sl), L.horizon)]
        return float(np.mean(x)), x.mean(axis=0)
    return m


def _float_floor(orig):
    def m(ctx, r):
        c = -float(np.mean(r.per_seed))
        return c > ctx.obj.floor, {"do_nothing": {"composite": c, "floor": ctx.obj.floor, "held": c > ctx.obj.floor}}
    return m


def _no_b5(orig):
    def m(values, sessions_left, out):
        Wm = W42
        sl = np.asarray(sessions_left)
        per = {k: np.asarray(v, float) for k, v in out.items()}
        per.update(Wm.bankroll_states(per, values["budgets"]["primary"]))
        caps = {r["name"]: (r["lo"], r["hi"]) for r in values["dimensions"]}
        c = 0.0
        for d in Wm.DIMENSIONS:
            if d.name in values["weights"]:
                lo, hi = caps[d.name]
                c = c + values["weights"][d.name] * Wm._z(d, per[d.key], lo, hi)[Wm._rows(sl, d.horizon)].mean(axis=0)
        return np.asarray(c, float)
    return m


def _accept_all(orig):
    """The plateau check skipped: a well-formed verdict accepting every candidate (its protocol and re-read limits the
    survey's own, so only the check itself is missing)."""
    def m(ctx, f):
        got = SV.read_design(ctx, f.design, ctx.ledger.reread, "reread")
        return type("V", (), dict(accepted=True, reason="mutant", rule="m", evaluated=0, held=0,
                                  protocol_sha256=ctx.spec.protocol_sha256, size_at=0.0, size_bound=0.0,
                                  size_label="mutant",
                                  reread_limits={n: {"value": float(got[n].value), "se": float(got[n].se)}
                                                 for n in ctx.limit_names}))()
    return m
_ALL_COMPLETE = (lambda o: (lambda ctx, starts: np.full(len(starts), len(ctx.calendar))))

#: name: (module, function mutated, how, the scenario that must catch it, the refusals it may raise)
MUTANTS = {
    "survey-seed": (SV, "draw_survey", lambda o: (lambda ctx: ctx.E.SS.Sampler(
        ctx.space, seed=ctx.spec.survey_seed + 1, method=ctx.spec.method).survey(
        ctx.spec.survey_n, ledger=ctx.ledger, protocol=ctx.protocol, reread_seeds=ctx.spec.reread_seeds,
        measures=ctx.limit_names, declaration_sha256=ctx.spec.protocol_sha256, max_proposals=ctx.spec.max_proposals)),
        "planted", ()),
    "schedule-fixed": (SV, "read_design", _fixed_schedule, "planted", ()),
    "reread-not-fresh": (SV, "read_design", lambda o: (lambda ctx, d, p, role: o(ctx, d, ctx.protocol, role)),
                         "planted", ("OffProtocol",)),
    "composite-sign": (SV, "composite", lambda o: (lambda ctx, arm, sl: -o(ctx, arm, sl)), "planted", ()),
    "b5-dropped": (W42, "composite_per_seed", _no_b5, "b5", ("SpecRefused",)),
    "rounds-skipped": (SV, "run_rounds", lambda o: (lambda ctx: None), "planted", ()),
    "order-reversed": (SV, "finalist_candidates", lambda o: (lambda ctx: list(reversed(sorted(
        {r.id: r for r in ctx.readings}.values(), key=lambda r: (float(r.value), r.id))))[:ctx.spec.candidates]),
        "planted", ()),
    "baselines-ignored": (SV, "beats_baselines", lambda o: (lambda ctx, got: (True, o(ctx, got)[1])), "noise", ()),
    "margin-ignored": (SV, "beats_baselines", lambda o: (lambda ctx, got: o(_with(ctx, delta=1e-12), got)), "near",
                       ()),
    "z-ignored": (SV, "beats_baselines", lambda o: (lambda ctx, got: o(_with(ctx, z=-8.0), got)), "near", ()),
    "t-as-normal": (SV, "t_threshold", lambda o: (lambda z, n: float(z)), "near6", ()),
    "first-baseline-only": (SV, "beats_baselines", lambda o: (lambda ctx, got: o(_with(
        ctx, baselines=ctx.spec.baselines[:1]), got)), "strong", ()),
    "limits-ignored": (SV, "limits_inside", lambda o: (lambda ctx, rr, sel: (True, o(ctx, rr, sel)[1])), "ceiling",
                       ()),
    "limit-direction-ignored": (SV, "limits_inside", lambda o: (lambda ctx, rr, sel: o(_with(ctx, limits=tuple(
        dict(x, direction="<=") for x in ctx.obj.limits)), rr, sel)), "floor", ()),
    "limits-from-selection": (SV, "limits_inside", lambda o: (lambda ctx, rr, sel: o(ctx, {**rr, **sel}, sel)),
                              "risky", ()),
    "limit-as-mean": (SV, "limit_value", _limit_as_mean, "tail", ()),
    "limit-horizon-ignored": (SV, "limit_value", lambda o: (lambda ctx, arm, sl, lim: o(
        ctx, arm, np.full(len(sl), len(ctx.calendar)), lim)), "censor", ()),
    "sessions-left-overstated": (SV, "sessions_left", _ALL_COMPLETE, "censor", ()),
    "calendar-unchecked": (SV, "sessions_left", lambda o: (lambda ctx, starts: np.array(
        [len(ctx.calendar) - ctx.calendar.index(d) if d in ctx.calendar else len(ctx.calendar) for d in starts])),
        "offcal", ()),
    "values-unchecked": (SV, "validate_values", lambda o: (lambda ctx, name, arm, sl: None), "range", ()),
    "crossing-critical-ignored": (SV, "crossing_check", lambda o: (lambda over, se, level, n: (
        over / se, bool(over / se > 0))), "crossing", ()),
    "no-harm-skipped": (SV, "no_harm", lambda o: (lambda ctx, out, sl: (True, o(ctx, out, sl)[1])), "harm_mid", ()),
    "no-harm-margin-x8": (SV, "no_harm", lambda o: (lambda ctx, out, sl: o(_with(
        ctx, no_harm_margin=8 * ctx.spec.no_harm_margin), out, sl)), "harm_mid", ()),
    "no-harm-margin-0": (SV, "no_harm", lambda o: (lambda ctx, out, sl: o(_with(ctx, no_harm_margin=0.0), out, sl)),
                         "harm_small", ()),
    "side-source-ignored": (SV, "no_harm", lambda o: (lambda ctx, out, sl: o(ctx, dataclasses.replace(
        out, side_source=SV.TRIGGER), sl)), "coin_side", ()),
    "do-nothing-floor-skipped": (SV, "do_nothing_floor", lambda o: (lambda ctx, r: (True, o(ctx, r)[1])), "meagre",
                                 ()),
    "do-nothing-not-before-ranking": (SV, "passes_floors", _floors_without("the do-nothing floor"), "meagre", ()),
    "do-nothing-by-float": (SV, "do_nothing_floor", _float_floor, "do_nothing_exact", ()),
    "not-paid-floor-skipped": (SV, "not_paid_floor", lambda o: (lambda ctx, got: (True, o(ctx, got)[1])), "unpaid",
                               ()),
    "not-paid-not-before-ranking": (SV, "passes_floors", _floors_without("the not_paid_within_B limit"), "unpaid",
                                    ()),
    "floors-after-ranking": (SV, "passes_floors", lambda o: (lambda ctx, got: (True, "", o(ctx, got)[2])), "mixed",
                             ()),
    "book-skipped": (SV, "book_check", lambda o: (lambda out: None), "hedge", ()),
    "overlap-admitted": (SV, "book_check", _overlap_admitted, "overlap", ()),
    "gate-skipped": (SV, "gate_check", lambda o: (lambda ctx, out: None), "gated", ()),
    "plateau-skipped": (SV, "plateau_step", _accept_all, "spike", ()),
    "check-output-dropped": (SV, "_check_output", lambda o: (lambda ctx, out, p: SV.sessions_left(ctx, out.starts)),
                             "realkeys", ()),
    "real-path-unchecked": (SV, "_check_real_path", lambda o: (lambda out, keys: None), "realkeys", ()),
    "held-out-not-first": (SV, "_held_out_first", lambda o: (lambda ctx, out: None), "heldout", ()),
    "engine-binding-not-compared": (SV, "engine_sha", lambda o: (lambda E: o(SV.Engine.default())), "engine_swap",
                                    ()),
    "reread-value-from-selection": (SV, "choose_finalists", _reread_from_selection, "planted", ()),
    "list-sha-from-declaration": (SV, "emit", lambda o: (lambda ctx, fin, **kw: {**o(ctx, fin, **kw),
                                                                                "list_sha256": ctx.sha}), "planted",
                                  ()),
}


def _killed(eng, tmp, roots, scenario: str, expected: tuple[str, ...]) -> bool:
    """Killed: the scenario's verdict is wrong, or the expected refusal is raised -- never any other exception."""
    classes = tuple(getattr(eng.SS, n, None) or getattr(SV, n) for n in expected)
    try:
        return not SCENARIOS[scenario](eng, tmp, roots)
    except classes or ():
        return True


@pytest.mark.parametrize("mutant", sorted(MUTANTS))
def test_a_mutation_of_each_step_is_killed(eng, tmp_path, roots, monkeypatch, mutant):
    mod, fn, how, scenario, expected = MUTANTS[mutant]
    monkeypatch.setattr(mod, fn, how(getattr(mod, fn)))
    assert _killed(eng, tmp_path, roots, scenario, expected), f"the mutant {mutant} survived"


# ------------------------------------------------------------------------------------------------ counts and bytes


def test_every_cell_is_counted_and_carries_its_protocol(eng, tmp_path, roots):
    ORDER.clear()
    W.GATE_SEEN.clear()
    out = survey(eng, tmp_path, roots, "plateau")
    led = out.ledger
    vrows = rows_of(out.variants_path)
    assert len(vrows) == len(led.rows) == out.counts["cells"]
    assert {r["params"]["_declaration_sha256"] for r in vrows} == {out.declaration_sha256}
    assert {r["params"]["_protocol_sha256"] for r in vrows} == {protocol_sha(eng)} == {led.protocol_sha256}
    roles = {r["role"] for r in led.rows}
    assert {"baseline", "survey", "round-1", "round-2"} <= roles and any(r.startswith("plateau:") for r in roles)
    cells = {r["id"] for r in led.rows if r["status"] == "proposed"}
    assert set(W.CALLS) <= cells and set(csv(out.readings_path)["id"]) <= cells
    man = json.loads((out.list_path.parent / (out.list_path.name + ".manifest.json")).read_text())
    p = man["parameters"]
    assert man["variant_count"] == out.counts["cells"] and p["bindings"] == out.bindings
    assert p["objective"]["values_sha256"] and p["no_harm"] == {"margin": W.NO_HARM_MARGIN, "margin_row": "fixture"}
    assert ORDER == ["F-99_survey_readings", "F-99_survey_candidates", "F-99_survey_finalists", "variants"]
    assert set(W.GATE_SEEN) == {("supply",)}
    detail = json.loads(csv(out.candidates_path)["detail"][0])
    assert "inactivity_guards" in detail and "vacuous_limits" in detail                                   # m-2
    lim = json.loads(csv(out.list_path)["limits"][0])
    assert {"check_t", "check_level", "crossing_shown", "selection_value", "vacuous"} <= set(lim["taken_mean_p10"])
    pl = [c["plateau"] for c in out.candidates if "plateau" in c]                   # Q-192b's verdict, recorded
    assert pl and all(x["protocol_sha256"] == protocol_sha(eng) and set(x["reread_limits"]) ==
                      {lm.name for lm in W42.LIMITS} and {"size_at", "size_bound", "size_label"} <= set(x) for x in pl)
    assert p["ledger"]["protocol_sha256"] == protocol_sha(eng) and p["ledger"]["declared"]
    assert audit(out) == []


def test_same_seeds_same_bytes(eng, tmp_path, roots):
    a = survey(eng, tmp_path / "a", roots, "plateau")
    b = survey(eng, tmp_path / "b", roots, "plateau")
    for p, q in ((a.list_path, b.list_path), (a.readings_path, b.readings_path),
                 (a.candidates_path, b.candidates_path)):
        assert p.read_bytes() == q.read_bytes()
    assert a.token == b.token and rows_of(a.variants_path) == rows_of(b.variants_path)


def test_one_ledger_a_run(eng, tmp_path, roots, monkeypatch):
    made = []
    init = eng.SS.CellLedger.__init__

    def counting(self, *a, **k):
        made.append(self)
        init(self, *a, **k)
    monkeypatch.setattr(eng.SS.CellLedger, "__init__", counting)
    out = survey(eng, tmp_path, roots, "noise")
    assert len(made) == 1 and made[0] is out.ledger


# ------------------------------------------------------------------------------------------------ the refusals


def test_unpinned_and_bad_fixtures_refuse(eng, tmp_path, roots):
    decl = declare(eng, tmp_path)
    with at(roots["default"]["root"]):
        for kw in ({}, {"pin_fixture": SV.FIXTURE_PREFIX + "0" * 64}):
            with pytest.raises(SV.NotPinned):
                SV.run_survey(decl, results_dir=tmp_path / "out", name="x", **kw)
        with pytest.raises(SV.NotPinned):
            SV.run_survey(decl, results_dir=tmp_path / "results", name="x", pin_fixture=SV.fixture_pin(decl))
    assert not (tmp_path / "out").exists()


def _pinned_root(eng, tmp: Path, roots, rows: str) -> tuple[Path, Path]:
    root = roots["default"]["root"]
    mine = root / "prereg" / "F-99_toy.md"
    mine.parent.mkdir(exist_ok=True)
    mine.write_bytes(declare(eng, tmp).read_bytes())
    (root / "DECISIONS.md").write_text(rows.replace("{sha}", R.sha256_lf(mine)), encoding="utf-8")
    return root, mine


def test_a_pin_comes_from_this_repository_only(eng, tmp_path, roots):
    root, mine = _pinned_root(eng, tmp_path, roots, "| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 "
                                                    "`{sha}` | t |\n")
    try:
        with pytest.raises(SV.NotPinned, match="not a file of this repository"):
            SV.run_survey(mine, results_dir=root / "results", name="x")              # ROOT is the real repository
        with at(root):
            with pytest.raises(SV.PartRefused, match="fixture pin"):
                SV.run_survey(mine, results_dir=root / "results", name="x", writer=local_writer)
            with pytest.raises(SV.NotPinned, match="fixture pin never"):
                SV.run_survey(mine, results_dir=tmp_path / "o2", name="x", pin_fixture=SV.fixture_pin(mine))
            with pytest.raises(SV.PartRefused, match="survey_run.py"):              # M-4: the entry script only
                SV.run_survey(mine, results_dir=root / "results", name="x")
            mine.write_bytes(mine.read_bytes() + b"\nedited after the pin\n")
            with pytest.raises(SV.NotPinned, match="a change"):
                SV.run_survey(mine, results_dir=root / "results", name="x")
    finally:
        (root / "DECISIONS.md").write_text("", encoding="utf-8")
        mine.unlink()


def test_under_a_pin_the_process_is_checked(eng, tmp_path, roots, monkeypatch):
    """M-4, each guard on its own (the entry script stood in): a clean run, untracked files counted, every bound module
    tracked inside the repository, results only under results/."""
    root, mine = _pinned_root(eng, tmp_path, roots, "| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 "
                                                    "`{sha}` | t |\n")
    untracked = SV.untracked_modules
    try:
        monkeypatch.setattr(SV.R, "_main_script", lambda: (root / SV.ENTRY_SCRIPT).resolve())
        with at(root):
            with pytest.raises(SV.PartRefused, match="clean run"):
                SV.run_survey(mine, results_dir=root / "results", name="x")
            monkeypatch.setattr(SV.R, "_clean_run", lambda repo, what: None)
            monkeypatch.setattr(SV, "tree_problems", lambda: ["extended/my_runner.py"])
            with pytest.raises(SV.PartRefused, match="untracked files counted"):
                SV.run_survey(mine, results_dir=root / "results", name="x")
            monkeypatch.setattr(SV, "tree_problems", lambda: [])
            with pytest.raises(SV.PartRefused, match="tracked"):             # the toy parts live in tests/
                SV.run_survey(mine, results_dir=root / "results", name="x")
            monkeypatch.setattr(SV, "untracked_modules", lambda mods: [])
            with pytest.raises(SV.PartRefused, match="writes only under"):
                SV.run_survey(mine, results_dir=root / "out", name="x")
        with at(root):                                                 # the toy parts lie outside this tree
            assert any("outside the repository" in x for x in untracked(["survey_world"]))
    finally:
        (root / "DECISIONS.md").write_text("", encoding="utf-8")
        mine.unlink()


def test_the_rows_are_checked(eng, tmp_path, roots):
    """C-1: the no-harm margin's row and the values' row exist, come before the declaration's pin row and carry the
    margin and the values file's sha256."""
    root = roots["default"]["root"]
    vsha = roots["default"]["values_sha256"]
    good = (f"| E-100 | 2026-11-20 | the no-harm margin is {W.NO_HARM_MARGIN} | t |\n"
            f"| E-101 | 2026-11-20 | W42-R1's values `results/w42_r1_values.csv` sha256 `{vsha}` | t |\n")
    over = {"no_harm": {"margin": W.NO_HARM_MARGIN, "margin_row": "E-100"}}
    cases = [(good, None), (good.replace(str(W.NO_HARM_MARGIN), "0.05"), "does not carry"),
             (good.replace(vsha, "0" * 64), "does not carry"), ("", "is not a row")]
    try:
        for text, err in cases:
            (root / "DECISIONS.md").write_text(text, encoding="utf-8")
            decl = declare(eng, tmp_path / str(len(text)) / (err or "ok"), values_row="E-101", spec_over=over)
            if err is None:
                out = run(eng, root, decl, tmp_path / "ok-out")
                assert out.counts["cells"] > 0
            else:
                with pytest.raises(SV.NotPinned, match=err):
                    run(eng, root, decl, tmp_path / "x")
        assert SV.load_spec(W.declaration(SV._block(decl.read_bytes())))
    finally:
        (root / "DECISIONS.md").write_text("", encoding="utf-8")


def _tamper(decl: Path, part: str, **params) -> None:
    s = SV._block(decl.read_bytes())
    s["parts"][part]["params"].update(params)
    decl.write_bytes(W.declaration(s).encode("utf-8"))


def test_a_part_off_its_binding_refuses(eng, tmp_path, roots):
    """F-2: a part's parameters changed after binding (the gate's floor, the runner's shift, every other part)."""
    for part, params in (("gate", {"floor": 0.0}), ("runner", {"shift": 1.5}), ("space", {"x_hi": 0.5}),
                         ("schedule_builder", {"x": 1}), ("playbook", {"style": "other"})):
        decl = declare(eng, tmp_path / part)
        _tamper(decl, part, **params)
        with pytest.raises(SV.PartRefused, match=part):
            run(eng, roots["default"]["root"], decl, tmp_path / part / "out")
        assert W.CALLS == [] and not (tmp_path / part / "out").exists()
    assert {"extended.survey", "extended.components", "extended.search_space"} <= set(SV.code_closure("survey_world"))


def test_data_and_the_space_digest_are_bound(eng, tmp_path, roots):
    """M-4: a declared data file that differs refuses; a space whose built digest differs refuses."""
    root = roots["default"]["root"]
    (root / "results" / "toy_data.csv").write_bytes(b"a\n1\n")
    parts = W.parts_of()
    parts["runner"]["data"] = {"results/toy_data.csv": SV._raw_sha(root / "results" / "toy_data.csv")}
    decl = declare(eng, tmp_path / "d", parts=parts)
    (root / "results" / "toy_data.csv").write_bytes(b"a\n2\n")
    with pytest.raises(SV.PartRefused, match="data file"):
        run(eng, root, decl, tmp_path / "d" / "out")
    decl = declare(eng, tmp_path / "s")
    s = SV._block(decl.read_bytes())
    s["parts"]["space"]["digest"] = "0" * 64
    s["parts"]["space"]["sha256"] = SV.part_sha({k: v for k, v in s["parts"]["space"].items() if k != "sha256"})
    decl.write_bytes(W.declaration(s).encode("utf-8"))
    with pytest.raises(SV.PartRefused, match="digest"):
        run(eng, root, decl, tmp_path / "s" / "out")


def test_the_objective_is_w42_r1s_file(eng, tmp_path, roots, monkeypatch):
    """C-1: the values file by name, its sidecar's sha256, script, rule id, values digest and rule module sha256; the
    public functions required; every limit set (m-2)."""
    import shutil
    base = roots["default"]["root"]
    root = tmp_path / "root"
    shutil.copytree(base / "results", root / "results")
    (root / "DECISIONS.md").write_text("", encoding="utf-8")
    side = root / "results" / (W42.OUTPUT_NAME + ".manifest.json")
    good = side.read_text(encoding="utf-8")
    with at(root):
        assert SV.load_objective(W42).floor
        for key, val, err in (("script", "scripts/other.py", "script"), ("sha256", "0" * 64, "file's sha256")):
            side.write_text(json.dumps({**json.loads(good), key: val}), encoding="utf-8")
            with pytest.raises(SV.SpecRefused, match=err):
                SV.load_objective(W42)
        for key, err in (("rule_module_sha256", "rule module"), ("values_sha256", "digest"), ("rule_id", "rule id")):
            m = json.loads(good)
            m["parameters"][key] = "x"
            side.write_text(json.dumps(m), encoding="utf-8")
            with pytest.raises(SV.SpecRefused, match=err):
                SV.load_objective(W42)
        side.write_text(good, encoding="utf-8")
        monkeypatch.delattr(W42, "limit_estimate")
        with pytest.raises(SV.PartRefused, match="public functions"):
            SV.load_objective(W42)
    with pytest.raises(SV.SpecRefused, match="not W42-R1's output"):
        (root / "results" / "bad.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        SV.read_values(root / "results" / "bad.csv")


def test_an_unset_limit_refuses(eng, tmp_path, roots, monkeypatch):
    """m-2: a limit W42-R1 did not set refuses the run (the values file rewritten, its sidecar made consistent)."""
    import shutil
    root = tmp_path / "root"
    shutil.copytree(roots["default"]["root"] / "results", root / "results")
    p = root / "results" / W42.OUTPUT_NAME
    v = SV.read_values(p)
    v["limits"]["values"] = [x for x in v["limits"]["values"] if x["name"] != "orders_max_p90"]
    df = pd.DataFrame({"key": sorted(v), "value_json": [json.dumps(v[k], sort_keys=True, separators=(",", ":"))
                                                       for k in sorted(v)]})
    p.write_bytes(df.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    side = Path(f"{p}.manifest.json")
    m = json.loads(side.read_text(encoding="utf-8"))
    m["sha256"] = SV._raw_sha(p)
    m["parameters"]["values_sha256"] = W42.Wave42Values(v).digest()
    side.write_text(json.dumps(m), encoding="utf-8")
    with at(root):
        with pytest.raises(SV.SpecRefused, match="not set"):
            SV.load_objective(W42)


def test_a_lever_outside_the_allowlist_refuses(eng, tmp_path, roots):
    """F-8: plain side levers (direction, fade, invert_trigger, bias) and any lever without a searched id."""
    for name, values, lever in (("direction", ["-1", "1"], ""), ("fade", ["no", "yes"], ""),
                                ("invert_trigger", ["no", "yes"], "side"), ("bias", ["up", "down"], "A99")):
        decl = declare(eng, tmp_path / name, space={"extra": [{"name": name, "values": values, "lever": lever}]})
        with pytest.raises(SV.PartRefused, match="allowlist"):
            run(eng, roots["default"]["root"], decl, tmp_path / name / "out")


def test_the_spec_is_exactly_its_form(eng, tmp_path):
    good = SV._block(declare(eng, tmp_path).read_bytes())
    SV.load_spec(W.declaration(good))
    fi, pl = good["finalists"], good["plateau"]
    bad = [dict(baselines={"names": ["naive_coin"], "seed": 13}),
           dict(baselines={"names": ["naive_coin", "p14", "p15", "my_weak"], "seed": 13}),
           dict(finalists=dict(fi, z=0)), dict(finalists=dict(fi, reread_seeds=[101, 300, 301, 302, 303])),
           dict(finalists=dict(fi, margin=0.1)),
           dict(plateau=dict(pl, rule=dict(pl["rule"], margin=0.1))),
           dict(plateau=dict(pl, rule=dict(pl["rule"], side="two_sided"))),
           dict(survey=dict(good["survey"], seed=11.5)), dict(prereg_id="RD-9"),
           dict(rounds={k: v for k, v in good["rounds"].items() if k != "kappa"}),
           dict(no_harm={"margin": 0.005}), dict(no_harm={"margin": -1.0, "margin_row": "E-1"}),
           dict(objective=dict(good["objective"], values_row="E-x")),
           dict(protocol={k: v for k, v in good["protocol"].items() if k != "sha256"}),
           dict(parts=dict(good["parts"], gate={k: v for k, v in good["parts"]["gate"].items() if k != "keys"})),
           dict(parts=dict(good["parts"], space={k: v for k, v in good["parts"]["space"].items() if k != "digest"}))]
    for over in bad:
        with pytest.raises(SV.SpecRefused):
            SV.load_spec(W.declaration({**good, **over}))
    with pytest.raises(SV.SpecRefused):
        SV.load_spec(W.declaration(good) + W.declaration(good))


def test_the_protocol_sha256_is_checked_before_any_cell(eng, tmp_path, roots):
    decl = declare(eng, tmp_path)
    s = SV._block(decl.read_bytes())
    s["protocol"]["sha256"] = "0" * 64
    decl.write_bytes(W.declaration(s).encode("utf-8"))
    with pytest.raises(SV.SpecRefused, match="protocol sha256"):
        run(eng, roots["default"]["root"], decl, tmp_path / "out")
    assert W.CALLS == [] and not (tmp_path / "out").exists()


@pytest.mark.parametrize("runner", [{"tag": "heldout_test"}, {"tag": "confirmation"},
                                    {"blocks": [["2022-01-03", "2024-06-28"]]}, {"horizon": 400},
                                    {"late_start": "2024-01-03"}],
                         ids=["heldout-tag", "confirm-tag", "held-out-block", "held-out-horizon", "held-out-start"])
def test_a_held_out_run_refuses_first(eng, tmp_path, roots, runner):
    """F-4: refused at the first run (a start after the search years too, M-3), before the book, the gate or any
    reading; the failure record and variants written, no readings."""
    with pytest.raises(eng.SS.HeldOutInput):
        survey(eng, tmp_path, roots, runner=dict(runner, kind="plateau"))
    out = tmp_path / "out"
    assert len(W.CALLS) == 1 and (out / "F-99_survey_failure.csv").is_file()
    assert not (out / "F-99_survey_readings.csv").exists() and rows_of(out / "variants.jsonl")


def test_a_held_out_protocol_refuses_before_any_cell(eng, tmp_path, roots):
    for i, pr in enumerate(({"blocks": [["2022-01-03", "2024-06-28"]]}, {"horizon": 1000})):
        with pytest.raises(eng.SS.HeldOutInput):
            survey(eng, tmp_path / str(i), roots, spec_over={"protocol": dict(W.SPEC["protocol"], **pr)})
        assert W.CALLS == [] and not (tmp_path / str(i) / "out").exists()


def test_a_held_out_variants_row_refuses_before_the_survey(eng, tmp_path, roots):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "variants.jsonl").write_text(json.dumps({"label": "heldout_test", "params": {}}) + "\n",
                                                     encoding="utf-8")
    with pytest.raises(SV.HeldOutRow):
        survey(eng, tmp_path, roots)
    assert W.CALLS == []
    assert SV.heldout_problems([{"label": "s", "params": {"day": "2024-01-02"}}])
    assert not SV.heldout_problems([{"label": "survey:proposed", "params": {"confirm_bars": 2, "judged_x": 1},
                                     "timestamp": "2026-11-21T03:00:00+00:00"}])                        # n-5


def test_a_second_run_refuses(eng, tmp_path, roots):
    """F-5, m-1: the same declaration again into the same folder, under the same name, or when the decision log names
    this run's outputs."""
    root = roots["default"]["root"]
    decl = declare(eng, tmp_path, "noise")
    run(eng, root, decl, tmp_path / "out")
    with at(root):
        with pytest.raises(SV.RunRepeated, match="run once"):
            SV.run_survey(decl, results_dir=tmp_path / "out", name="F-99_again", pin_fixture=SV.fixture_pin(decl),
                          engine=eng, writer=local_writer, variants_writer=local_variants)
    with pytest.raises(SV.RunRepeated, match="never overwritten"):
        run(eng, root, decl, tmp_path / "out")
    try:
        (root / "DECISIONS.md").write_text("| E-500 | 2026-11-21 | the survey `F-99_survey_finalists.csv` | t |\n",
                                           encoding="utf-8")
        with pytest.raises(SV.RunRepeated, match="already records"):
            run(eng, root, decl, tmp_path / "fresh")
    finally:
        (root / "DECISIONS.md").write_text("", encoding="utf-8")


def test_a_refusal_after_the_first_cell_writes_variants_first(eng, tmp_path, roots):
    """m-4, F-6: a plateau rule leaving a lever unstepped refuses after every read; the variants rows first, and even
    when the failure record cannot be written."""
    rule = dict(W.SPEC["plateau"]["rule"], steps={"x": 0.1, "y": 2})
    over = {"plateau": dict(W.SPEC["plateau"], rule=rule)}
    ORDER.clear()
    with pytest.raises(eng.PL.PlateauRefused):
        survey(eng, tmp_path / "a", roots, spec_over=over)
    out = tmp_path / "a" / "out"
    fail = csv(out / "F-99_survey_failure.csv")
    assert ORDER == ["variants", "F-99_survey_failure"]
    assert len(rows_of(out / "variants.jsonl")) == json.loads(fail["counts"][0])["cells"] > 0

    def broken(df, name, **kw):
        if name.endswith("_failure"):
            raise OSError("the disk is full")
        return local_writer(df, name, **kw)
    decl = declare(eng, tmp_path / "b", spec_over=over)
    with pytest.raises(eng.PL.PlateauRefused) as e:
        run(eng, roots["default"]["root"], decl, tmp_path / "b" / "out", writer=broken)
    assert rows_of(tmp_path / "b" / "out" / "variants.jsonl")
    assert any("failure record could not be written" in n for n in getattr(e.value, "__notes__", []))


def test_an_engine_without_q192b_refuses(eng, tmp_path, roots, monkeypatch):
    """An engine whose ledger refuses a limit on the re-read seeds (Q-192 before Q-192b, stood in here) refuses."""
    real = eng.SS.CellLedger.protocol_for

    def before_q192b(self, measure=None, *, reread=False):
        if reread and measure is not None and measure != self.protocol.measure:
            raise eng.SS.OffProtocol("a limit on the re-read seeds (the engine before Q-192b)")
        return real(self, measure, reread=reread)
    monkeypatch.setattr(eng.SS.CellLedger, "protocol_for", before_q192b)
    with pytest.raises(SV.PartRefused, match="Q-192b"):
        survey(eng, tmp_path, roots)
    assert W.CALLS == []


def test_an_engine_without_q192_refuses(eng):
    class Old:
        SS = type("SS", (), {"Sampler": type("S", (), {"survey": lambda self, n, *, ledger: None}),
                             "admit_one": staticmethod(lambda r, *, ledger, protocol: r),
                             "CellLedger": type("L", (), {"begin": lambda self, role, seed: None})})
    with pytest.raises(SV.PartRefused, match=SV.ENGINE_COMMIT):
        SV.Engine(Old.SS, eng.P, eng.PL).check()


def test_the_entry_script_takes_one_declaration(tmp_path):
    r = subprocess.run([sys.executable, str(REPO / SV.ENTRY_SCRIPT)], cwd=REPO, capture_output=True, text=True,
                       timeout=120)
    assert r.returncode == 2 and "usage" in r.stderr.lower()
    r = subprocess.run([sys.executable, str(REPO / SV.ENTRY_SCRIPT), "a.md", "b.md"], cwd=REPO, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 2


# ------------------------------------------------------------------------------------------------ the defaults


def test_the_default_writers_in_a_process_of_their_own(tmp_path):
    """`extended.results.write_result` and the vendored `VariantCounter` (the defaults) under a fixture pin, the
    vendored tree on sys.path: its own process."""
    code = textwrap.dedent(f"""
        import sys, json
        from pathlib import Path
        sys.path.insert(0, {str(REPO / 'tests')!r})
        import survey_world as W
        W42, APPLY = W.load_w42()
        from extended import survey as SV
        E = SV.Engine.default()
        tmp = Path({str(tmp_path)!r})
        root = tmp / "root"; W.w42_root(root)
        p = E.SS.Protocol("composite", tuple(tuple(b) for b in W.SPEC["protocol"]["blocks"]),
                          tuple(W.SPEC["protocol"]["seeds"]), 0)
        psha = E.SS.protocol_sha256(p, tuple(W.SPEC["finalists"]["reread_seeds"]), tuple(l.name for l in W42.LIMITS))
        s = W.spec(SV.declare_parts(W.parts_of("plateau"), E), protocol_sha256=psha, code_sha256=SV.objective_code_sha())
        decl = tmp / "F-99_decl.md"; decl.write_bytes(W.declaration(s).encode())
        SV.ROOT = root
        out = SV.run_survey(decl, results_dir=tmp / "out", name="F-99_s", pin_fixture=SV.fixture_pin(decl))
        from extended.results import verify_result
        print(json.dumps({{"ok": [verify_result(q)[0] for q in (out.list_path, out.readings_path,
                                                                out.candidates_path)],
                           "finalists": len(out.finalists), "cells": out.counts["cells"],
                           "variants": len((tmp / "out" / "variants.jsonl").read_text().splitlines())}}))
    """)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True, timeout=600, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["ok"] == [True, True, True] and got["finalists"] >= 1 and got["variants"] == got["cells"]
