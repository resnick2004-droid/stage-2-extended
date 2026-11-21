"""Wave 5's survey runner (`extended/survey.py`), end to end on the synthetic worlds of `tests/survey_world.py`, over
Wave 3.4's engine (with Q-192's re-read of the limits stood in, `survey_world.q192_protocol_for`) and W42-R1's own
module and rule (a fixture result file from its `setting_rule` on toy H4-shaped baselines). No bar, no result file of
the repository: every output goes to a temporary folder.

* the planted region is found within the declared budget; in every other world (noise, a spike, a near miss, a
  stronger baseline, a crossed ceiling or floor, a floor crossed on the fresh seeds only, a harmful or coin-chosen
  side, a hedge or an overlap across accounts, a refused gate) there is no finalist, each world checked to bite;
* the survey's composite is W42-R1's, by its own functions, on its own baselines;
* every cell is counted, the variants rows carry the declaration's and protocol's sha256 and are written last;
* the refusals: unpinned, bad fixtures, a pin outside this repository, a part or the engine off its binding, a part's
  parameters changed after binding, a searched lever outside the allowlist, a spec off its form, a held-out run (first,
  before the book and the gate), block, horizon or variants row, a second run, an engine without Q-192;
* a mutation of each step is killed by its scenario's own verdict, an exception counting only when it is the expected
  refusal (S-2, F-9).
"""
from __future__ import annotations

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

from extended import ROOT
from extended import reader as R

import survey_world as W   # noqa: E402  (tests/ is on sys.path under pytest's rootdir)

W.load_wave42()
from extended import survey as SV  # noqa: E402


@pytest.fixture(scope="module")
def eng():
    E = SV.Engine.default()
    E.check()
    return E


@pytest.fixture(autouse=True)
def q192(eng, monkeypatch):
    monkeypatch.setattr(eng.SS.CellLedger, "protocol_for", W.q192_protocol_for(eng.SS.CellLedger.protocol_for))


@pytest.fixture(scope="module")
def w42(tmp_path_factory):
    out = {}
    for tag, spread, base in (("", 0.0, 0.0), ("_wide", 0.2, 0.0), ("_rare", 0.0, RARE_Q)):
        p = tmp_path_factory.mktemp("w42") / f"w42_r1{tag}.json"
        values = W.w42_fixture(p, spread, base)
        out[tag] = {"rule_id": "W42-R1", "file": str(p), "sha256": R.sha256_lf(p), "code_sha256": SV.w42_code_sha(),
                    "_values": values}
    out[""]["_wide"], out[""]["_rare"] = out["_wide"], out["_rare"]
    return out[""]


RARE_Q = -2.5      # baselines and designs whose payouts are rare: the do-nothing design outranks a baseline (V-4)


def objective(w42):
    return {k: v for k, v in w42.items() if not k.startswith("_")}


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


def declare(eng, tmp: Path, w42, kind="plateau", *, spec_over=None, parts=None, **part_kw) -> Path:
    block = SV.declare_parts(parts or W.parts_of(kind, **part_kw), eng)
    s = W.spec(block, objective(w42), **(spec_over or {}))
    (tmp / "decl").mkdir(parents=True, exist_ok=True)
    decl = tmp / "decl" / "F-99_decl.md"
    decl.write_bytes(W.declaration(s).encode("utf-8"))
    return decl


def run(eng, decl: Path, out: Path, **kw):
    W.CALLS.clear()
    kw.setdefault("engine", eng)
    return SV.run_survey(decl, results_dir=out, name="F-99_survey", pin_fixture=SV.fixture_pin(decl),
                         writer=local_writer, variants_writer=local_variants, **kw)


def survey(eng, tmp: Path, w42, kind="plateau", **kw):
    return run(eng, declare(eng, tmp, w42, kind, **kw), tmp / "out")


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
                    not f["plateau"]["accepted"]:
                probs.append(f"finalist {f['id']} is outside a limit, the no-harm floor or a plateau")
    elif out.token is not None or len(lst):
        probs.append("no finalist, but a token or a list row")
    if len(lst) != len(out.finalists) or len(csv(out.candidates_path)) != len(out.candidates) + len(out.floored):
        probs.append("the list or the candidates file does not hold the run's")
    return probs


def in_region(design) -> bool:
    return W.bump(design) >= 0.5 * W.A


def reasons(out) -> str:
    return " | ".join(str(c.get("reason", "")) for c in out.candidates + out.floored)


# ------------------------------------------------------------------------------------------------ the scenarios
# Each returns True when the survey behaves correctly in its world, and checks that the world bites.


def sc_planted(eng, tmp, w42):
    out = survey(eng, tmp, w42, "plateau")
    return bool(out.finalists) and all(in_region(f["design"]) for f in out.finalists) and audit(out) == []


def _none(kind, bite, wide=False, **runner):
    def sc(eng, tmp, w42):
        w42 = w42["_wide"] if wide else w42
        params = dict(runner, kind=kind)
        if "harm" in params:
            params.update(harm=params["harm"] * W.NO_HARM_MARGIN, steady_weight=w42["_values"]["weights"]["steady"])
        out = survey(eng, tmp, w42, kind, runner=params)
        return out.finalists == [] and audit(out) == [] and bite(out, w42)
    return sc


def _spike_bites(out, w42):
    return any("plateau" in c for c in out.candidates if abs(c["design"]["x"] - 0.3) < 1e-9)


def _near_bites(out, w42):  # a candidate past delta* on every gap and past the t threshold without it, yet not with it
    d = w42["_values"]["delta_star"]["value"]
    return any(c.get("gaps") and all(g["gap"] > d and g["gap"] / g["se"] > g["threshold"] for g in c["gaps"].values())
               for c in out.candidates)


def _strong_bites(out, w42):   # a candidate beats the naive coin but not P-16
    return any(c.get("gaps") and c["gaps"]["naive_coin"]["beaten"] and not c["gaps"]["p16"]["beaten"]
               for c in out.candidates)


def _limit_bites(name, selection_inside=False):
    def bite(out, w42):
        hit = [c for c in out.candidates if c.get("limits") and not c["limits"][name]["inside"]
               and all(g["beaten"] for g in c["gaps"].values())]
        return bool(hit) and (not selection_inside or any(
            (c["limits"][name]["selection_value"] >= c["limits"][name]["bound"]) for c in hit))
    return bite


def _refused_rows(cls):
    def bite(out, w42):
        return any(r.startswith(cls) for r in csv(out.readings_path)["refused"])
    return bite


def sc_harm_small(eng, tmp, w42):
    """The as-traded side worse by half the margin: inside the floor, so the planted finalists stand."""
    out = survey(eng, tmp, w42, "harm", runner={"kind": "harm", "harm": 0.5 * W.NO_HARM_MARGIN,
                                                "steady_weight": w42["_values"]["weights"]["steady"]})
    return bool(out.finalists) and all(-W.NO_HARM_MARGIN < f["no_harm"]["as_traded_minus_reflected"] < 0
                                       for f in out.finalists) and audit(out) == []


def _refusal(kind, cls, word):
    def sc(eng, tmp, w42):
        try:
            survey(eng, tmp, w42, kind)
        except cls as e:
            return word in str(e)
        return False
    return sc


def sc_heldout_gated(eng, tmp, w42):
    """F-4: the gated designs' runs labelled held-out -- the whole run refuses at the first, before the gate."""
    try:
        survey(eng, tmp, w42, "gated", runner={"kind": "gated", "hot_tag": "heldout_2024"})
    except eng.SS.HeldOutInput:
        out = tmp / "out"
        return (out / "F-99_survey_failure.csv").is_file() and (out / "variants.jsonl").is_file() and \
            not (out / "F-99_survey_readings.csv").exists()
    return False


def sc_engine_swap(eng, tmp, w42):
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
            run(eng, declare(eng, tmp, w42), tmp / "out", engine=SV.Engine(eng.SS, eng.P, mod))
        except SV.PartRefused as e:
            return "engine" in str(e)
        return False
    finally:
        sys.modules.pop("extended.plateau_changed", None)


def sc_identity(eng, tmp, w42):
    """The survey's composite is W42-R1's: on the fixture's own baselines it gives the rule's composite values; on an
    arm far outside the caps it gives the hand formula (clipped, oriented, weighted, each dimension over its starts)."""
    Wm = W.load_wave42()
    v = w42["_values"]
    seeds, n = list(range(901, 917)), 40
    sl = tuple(range(420, 420 - 10 * n, -10))
    ctx = type("C", (), {})()
    ctx.W, ctx.obj = Wm, SV.load_objective(objective(w42), fixture=True)
    base = W.baseline_values(seeds, n)
    ok = all(abs(float(np.mean(SV.composite(ctx, base[b], sl))) - v["composite"]["value"][b]) < 1e-12
             for b in SV.BASELINES)
    arm = {k: x * 3.0 + 50.0 for k, x in W.unit_values("extreme", 0.0, seeds, n).items()}
    arm["share_months_positive"] = np.clip(arm["share_months_positive"] - 60.0, -1.0, 2.0)
    per = dict(arm)
    per.update(Wm._derived(arm, v["budgets"]["primary"]))
    want = 0.0
    for d in v["dimensions"]:
        if d["name"] not in v["weights"]:
            continue
        rows = np.asarray(sl) >= d["horizon"]
        u = np.clip((per[d["key"]][rows] - d["lo"]) / (d["hi"] - d["lo"]), 0.0, 1.0)
        want = want + v["weights"][d["name"]] * (u if d["direction"] == "higher" else 1.0 - u).mean(axis=0)
    return ok and np.allclose(SV.composite(ctx, arm, sl), want, rtol=0, atol=1e-12)


def sc_nothing(eng, tmp, w42):
    """V-4: with rare payouts the do-nothing design outranks a baseline (W42-R1's own values); a region of designs that
    buy nothing is floored before ranking and never a finalist."""
    rare = w42["_rare"]
    dn = rare["_values"]["do_nothing"]["composite"]
    outranks = dn > min(rare["_values"]["composite"]["value"].values())
    out = survey(eng, tmp, rare, "nothing", runner={"kind": "nothing", "base_q": RARE_Q})
    hit = [f for f in out.floored if abs(f["do_nothing"]["composite"] - dn) < 1e-9]
    return outranks and out.finalists == [] and bool(hit) and audit(out) == [] and         all(abs(-c["selection_value"] - dn) > 1e-9 for c in out.candidates)


def sc_mixed(eng, tmp, w42):
    """V-4's order: designs failing the no-harm floor outrank the good ones; floored first, the good ones are ranked."""
    out = survey(eng, tmp, w42, "mixed", runner={"kind": "mixed", "harm": 1.5 * W.NO_HARM_MARGIN,
                                                  "steady_weight": w42["_values"]["weights"]["steady"]})
    harmed = [f for f in out.floored if "no-harm" in f["reason"]]
    best = min((f["selection_value"] for f in out.finalists), default=None)
    return bool(out.finalists) and all(f["design"]["k"] == "a" for f in out.finalists) and         best is not None and any(h["selection_value"] < best for h in harmed) and audit(out) == []


def sc_do_nothing_unit(eng, tmp, w42):
    """The do-nothing floor is strict: a composite equal to the do-nothing design's is refused, one above it kept."""
    ctx = type("C", (), {})()
    ctx.obj = SV.load_objective(objective(w42), fixture=True)
    at = type("Rd", (), {"value": -ctx.obj.do_nothing})()
    above = type("Rd", (), {"value": -(ctx.obj.do_nothing + 1e-6)})()
    return SV.do_nothing_floor(ctx, at)[0] is False and SV.do_nothing_floor(ctx, above)[0] is True


def sc_crossing(eng, tmp, w42):
    """The one-sided check beside a limit: a small excess within the t critical value is not shown; a large one is."""
    return SV.crossing_check(0.5, 1.0, 0.05, 32)[1] is False and SV.crossing_check(3.0, 1.0, 0.05, 32)[1] is True


SCENARIOS = {
    "planted": sc_planted,
    "noise": _none("noise", lambda out, w: len(out.candidates) == W.SPEC["finalists"]["candidates"]),
    "spike": _none("spike", _spike_bites),
    "near": _none("near", _near_bites, wide=True),
    "strong": _none("strong", _strong_bites),
    "ceiling": _none("ceiling", _limit_bites("accounts_max_p90")),
    "floor": _none("floor", _limit_bites("taken_mean_p10")),
    "risky": _none("risky", _limit_bites("taken_mean_p10", selection_inside=True)),
    "harm_mid": _none("harm", lambda out, w: "no-harm" in reasons(out), harm=1.5),
    "harm_small": sc_harm_small,
    "coin_side": _none("coin_side", lambda out, w: "no-harm" in reasons(out)),
    "hedge": _none("hedge", _refused_rows("tier1")),
    "overlap": _none("overlap", _refused_rows("overlap")),
    "gated": _none("gated", _refused_rows("gate")),
    "unpaired": _refusal("unpaired", SV.SurveyRefused, "paired"),
    "realkeys": _refusal("realkeys", SV.SurveyRefused, "real path"),
    "heldout": sc_heldout_gated,
    "engine_swap": sc_engine_swap,
    "identity": sc_identity,
    "crossing": sc_crossing,
    "nothing": sc_nothing,
    "mixed": sc_mixed,
    "do_nothing_unit": sc_do_nothing_unit,
}


def test_every_scenario_behaves_unmutated(eng, tmp_path, w42):
    """The kill tests' control: each world, unmutated, gives the correct verdict and bites."""
    bad = [name for name, sc in SCENARIOS.items() if not sc(eng, tmp_path / name, w42)]
    assert bad == []


# ------------------------------------------------------------------------------------------------ the mutations


def _with(ctx, **kw):
    c = copy.copy(ctx)
    for k, v in kw.items():
        if k in {f.name for f in dataclasses.fields(ctx.spec)}:
            c.spec = dataclasses.replace(c.spec, **{k: v})
        else:
            c.obj = dataclasses.replace(c.obj, **{k: v})
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


def _composite_flaw(flaw):
    def make(orig):
        def composite(ctx, arm, sl):
            Wm, ob = ctx.W, ctx.obj
            per = dict(arm)
            per.update(Wm._derived({k: np.asarray(x, float) for k, x in arm.items()}, ob.budget))
            c = 0.0
            for dim, lo, hi, w in ob.dims:
                rows = Wm._rows(np.asarray(sl), dim.horizon)
                u = (np.asarray(per[dim.key], float)[rows] - lo) / (hi - lo)
                u = u if flaw == "unclipped" else np.clip(u, 0.0, 1.0)
                z = u if (flaw == "direction" or dim.direction > 0) else 1.0 - u
                c = c + (1.0 if flaw == "weights" else w) * z.mean(axis=0)
            return np.asarray(c, float)
        return composite
    return make


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


_ACCEPT = type("V", (), dict(accepted=True, reason="mutant", rule="m", evaluated=0, held=0))

#: name: (the function of extended/survey.py mutated, how, the scenario that must catch it, the refusal it may raise)
MUTANTS = {
    "survey-seed": ("draw_survey", lambda o: (lambda ctx: ctx.E.SS.Sampler(
        ctx.space, seed=ctx.spec.survey_seed + 1, method=ctx.spec.method).survey(
        ctx.spec.survey_n, ledger=ctx.ledger, protocol=ctx.protocol, reread_seeds=ctx.spec.reread_seeds,
        measures=ctx.limit_names, max_proposals=ctx.spec.max_proposals)), "planted", ()),
    "schedule-fixed": ("read_design", _fixed_schedule, "planted", ()),
    "reread-not-fresh": ("read_design", lambda o: (lambda ctx, d, p, role: o(ctx, d, ctx.protocol, role)), "planted",
                         ("OffProtocol",)),
    "composite-sign": ("composite", lambda o: (lambda ctx, arm, sl: -o(ctx, arm, sl)), "planted", ()),
    "composite-weights-ignored": ("composite", _composite_flaw("weights"), "identity", ()),
    "composite-direction-ignored": ("composite", _composite_flaw("direction"), "identity", ()),
    "composite-unclipped": ("composite", _composite_flaw("unclipped"), "identity", ()),
    "rounds-skipped": ("run_rounds", lambda o: (lambda ctx: None), "planted", ()),
    "order-reversed": ("finalist_candidates", lambda o: (lambda ctx: list(reversed(sorted(
        {r.id: r for r in ctx.readings}.values(), key=lambda r: (float(r.value), r.id))))[:ctx.spec.candidates]),
        "planted", ()),
    "baselines-ignored": ("beats_baselines", lambda o: (lambda ctx, got: (True, o(ctx, got)[1])), "noise", ()),
    "margin-ignored": ("beats_baselines", lambda o: (lambda ctx, got: o(_with(ctx, delta=1e-12), got)), "near", ()),
    "z-ignored": ("beats_baselines", lambda o: (lambda ctx, got: o(_with(ctx, z=-8.0), got)), "near", ()),
    "first-baseline-only": ("beats_baselines", lambda o: (lambda ctx, got: o(_with(
        ctx, baselines=ctx.spec.baselines[:1]), got)), "strong", ()),
    "limits-ignored": ("limits_inside", lambda o: (lambda ctx, rr, sel: (True, o(ctx, rr, sel)[1])), "ceiling", ()),
    "limit-direction-ignored": ("limits_inside", lambda o: (lambda ctx, rr, sel: o(_with(ctx, limits=tuple(
        dict(x, direction="<=") for x in ctx.obj.limits)), rr, sel)), "floor", ()),
    "limits-from-selection": ("limits_inside", lambda o: (lambda ctx, rr, sel: o(ctx, {**rr, **sel}, sel)), "risky",
                              ()),
    "crossing-critical-ignored": ("crossing_check", lambda o: (lambda over, se, level, n: (
        over / se, bool(over / se > 0))), "crossing", ()),
    "no-harm-skipped": ("no_harm", lambda o: (lambda ctx, out: (True, o(ctx, out)[1])), "harm_mid", ()),
    "no-harm-margin-x8": ("no_harm", lambda o: (lambda ctx, out: o(_with(
        ctx, no_harm_margin=8 * ctx.obj.no_harm_margin), out)), "harm_mid", ()),
    "no-harm-margin-0": ("no_harm", lambda o: (lambda ctx, out: o(_with(ctx, no_harm_margin=0.0), out)),
                         "harm_small", ()),
    "side-source-ignored": ("no_harm", lambda o: (lambda ctx, out: o(ctx, dataclasses.replace(
        out, side_source=SV.TRIGGER))), "coin_side", ()),
    "book-skipped": ("book_check", lambda o: (lambda out: None), "hedge", ()),
    "overlap-admitted": ("book_check", _overlap_admitted, "overlap", ()),
    "gate-skipped": ("gate_check", lambda o: (lambda ctx, out: None), "gated", ()),
    "do-nothing-floor-skipped": ("do_nothing_floor", lambda o: (lambda ctx, r: (True, o(ctx, r)[1])),
                                 "do_nothing_unit", ()),
    "floors-after-ranking": ("passes_floors", lambda o: (lambda ctx, got: (True, "", o(ctx, got)[2])), "mixed", ()),
    "plateau-skipped": ("plateau_step", lambda o: (lambda ctx, f: _ACCEPT()), "spike", ()),
    "check-output-dropped": ("_check_output", lambda o: (lambda ctx, out, p: None), "realkeys", ()),
    "real-path-unchecked": ("_check_real_path", lambda o: (lambda out, keys: None), "realkeys", ()),
    "held-out-not-first": ("_held_out_first", lambda o: (lambda ctx, out: None), "heldout", ()),
    "engine-binding-not-compared": ("engine_sha", lambda o: (lambda E: o(SV.Engine.default())), "engine_swap", ()),
    "reread-value-from-selection": ("choose_finalists", _reread_from_selection, "planted", ()),
    "list-sha-from-declaration": ("emit", lambda o: (lambda ctx, fin, **kw: {**o(ctx, fin, **kw),
                                                                            "list_sha256": ctx.sha}), "planted", ()),
}


def _killed(eng, tmp, w42, scenario: str, expected: tuple[str, ...]) -> bool:
    """Killed: the scenario's verdict is wrong, or the expected refusal is raised -- never any other exception."""
    classes = tuple(getattr(eng.SS, n) for n in expected)
    try:
        return not SCENARIOS[scenario](eng, tmp, w42)
    except classes or ():
        return True


@pytest.mark.parametrize("mutant", sorted(MUTANTS))
def test_a_mutation_of_each_step_is_killed(eng, tmp_path, w42, monkeypatch, mutant):
    fn, how, scenario, expected = MUTANTS[mutant]
    monkeypatch.setattr(SV, fn, how(getattr(SV, fn)))
    assert _killed(eng, tmp_path, w42, scenario, expected), f"the mutant {mutant} survived"


# ------------------------------------------------------------------------------------------------ counts and bytes


def test_every_cell_is_counted_and_carries_its_protocol(eng, tmp_path, w42):
    ORDER.clear()
    W.GATE_SEEN.clear()
    out = survey(eng, tmp_path, w42, "plateau")
    led = out.ledger
    vrows = rows_of(out.variants_path)
    assert len(vrows) == len(led.rows) == out.counts["cells"]
    assert {r["params"]["_declaration_sha256"] for r in vrows} == {out.declaration_sha256}
    assert {r["params"]["_protocol_sha256"] for r in vrows} == {SV.protocol_digest(led.protocol)}
    roles = {r["role"] for r in led.rows}
    assert {"baseline", "survey", "round-1", "round-2"} <= roles and any(r.startswith("plateau:") for r in roles)
    cells = {r["id"] for r in led.rows if r["status"] == "proposed"}
    assert set(W.CALLS) <= cells and set(csv(out.readings_path)["id"]) <= cells
    man = json.loads((out.list_path.parent / (out.list_path.name + ".manifest.json")).read_text())
    assert man["variant_count"] == out.counts["cells"]
    p = man["parameters"]
    assert p["bindings"] == out.bindings and p["pin_row"] == "fixture" and p["objective_sha256"] == w42["sha256"]
    assert ORDER == ["F-99_survey_readings", "F-99_survey_candidates", "F-99_survey_finalists", "variants"]
    assert set(W.GATE_SEEN) == {("supply",)}                        # F-10: the gate sees its declared keys only
    assert any(r.endswith(":baseline") for r in csv(out.readings_path)["role"])          # n-e
    lst = csv(out.list_path)
    assert all(lst["playbook_sha256"]) and all("trigger" in t for t in lst["playbook"])
    lim = json.loads(lst["limits"][0])
    assert {"check_t", "check_level", "crossing_shown", "selection_value"} <= set(lim["taken_mean_p10"])
    assert audit(out) == []


def test_same_seeds_same_bytes(eng, tmp_path, w42):
    a = survey(eng, tmp_path / "a", w42, "plateau")
    b = survey(eng, tmp_path / "b", w42, "plateau")
    for p, q in ((a.list_path, b.list_path), (a.readings_path, b.readings_path),
                 (a.candidates_path, b.candidates_path)):
        assert p.read_bytes() == q.read_bytes()
    assert a.token == b.token and rows_of(a.variants_path) == rows_of(b.variants_path)


def test_one_ledger_a_run(eng, tmp_path, w42, monkeypatch):
    made = []
    init = eng.SS.CellLedger.__init__

    def counting(self, *a, **k):
        made.append(self)
        init(self, *a, **k)
    monkeypatch.setattr(eng.SS.CellLedger, "__init__", counting)
    out = survey(eng, tmp_path, w42, "noise")
    assert len(made) == 1 and made[0] is out.ledger


# ------------------------------------------------------------------------------------------------ the refusals


def test_unpinned_and_bad_fixtures_refuse(eng, tmp_path, w42):
    decl = declare(eng, tmp_path, w42)
    for kw in ({}, {"pin_fixture": SV.FIXTURE_PREFIX + "0" * 64}):
        with pytest.raises(SV.NotPinned):
            SV.run_survey(decl, results_dir=tmp_path / "out", name="x", **kw)
    with pytest.raises(SV.NotPinned):
        SV.run_survey(decl, results_dir=tmp_path / "results", name="x", pin_fixture=SV.fixture_pin(decl))
    assert not (tmp_path / "out").exists()


def test_a_pin_comes_from_this_repository_only(eng, tmp_path, w42, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "prereg").mkdir(parents=True)
    mine = repo / "prereg" / "F-99_toy.md"
    mine.write_bytes(declare(eng, tmp_path, w42).read_bytes())
    (repo / "DECISIONS.md").write_text(f"| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 "
                                       f"`{R.sha256_lf(mine)}` | t |\n", encoding="utf-8")
    with pytest.raises(SV.NotPinned, match="not a file of this repository"):
        SV.run_survey(mine, results_dir=repo / "out", name="x")
    monkeypatch.setattr(SV, "ROOT", repo)
    with pytest.raises(SV.NotPinned, match="inside this repository"):
        SV.run_survey(mine, results_dir=tmp_path / "elsewhere", name="x")
    with pytest.raises(SV.PartRefused, match="fixture pin"):
        SV.run_survey(mine, results_dir=repo / "out", name="x", writer=local_writer)
    with pytest.raises(SV.NotPinned, match="fixture pin never"):
        SV.run_survey(mine, results_dir=tmp_path / "o2", name="x", pin_fixture=SV.fixture_pin(mine))
    mine.write_bytes(mine.read_bytes() + b"\nedited after the pin\n")
    with pytest.raises(SV.NotPinned, match="a change"):
        SV.run_survey(mine, results_dir=repo / "out", name="x")


def _tamper(decl: Path, part: str, **params) -> None:
    s = SV._block(decl.read_bytes())
    s["parts"][part]["params"].update(params)
    decl.write_bytes(W.declaration(s).encode("utf-8"))


def test_a_part_off_its_binding_refuses(eng, tmp_path, w42):
    """F-2: a part's parameters changed after binding (the note's make_gate 0.5 against 0.0, the runner's shift 0
    against 1.5, every other part likewise), or a part's code changed, refuses; nothing is run or written."""
    for part, params in (("gate", {"floor": 0.0}), ("runner", {"shift": 1.5}), ("space", {"x_hi": 0.5}),
                         ("schedule_builder", {"x": 1}), ("playbook", {"style": "other"})):
        decl = declare(eng, tmp_path / part, w42)
        _tamper(decl, part, **params)
        W.CALLS.clear()
        with pytest.raises(SV.PartRefused, match=part):
            run(eng, decl, tmp_path / part / "out")
        assert W.CALLS == [] and not (tmp_path / part / "out").exists()
    a = SV.part_sha({"id": "survey_world:make_gate", "params": {"floor": 0.5}, "keys": ["supply"]})
    b = SV.part_sha({"id": "survey_world:make_gate", "params": {"floor": 0.0}, "keys": ["supply"]})
    assert a != b
    closure = SV.code_closure("survey_world")
    assert {"extended.survey", "extended.components", "extended.search_space"} <= set(closure)


def test_the_objective_and_its_code_are_bound(eng, tmp_path, w42):
    decl = declare(eng, tmp_path, w42)
    s = SV._block(decl.read_bytes())
    for key, val in (("sha256", "0" * 64), ("code_sha256", "0" * 64)):
        t = copy.deepcopy(s)
        t["objective"][key] = val
        decl.write_bytes(W.declaration(t).encode("utf-8"))
        with pytest.raises((SV.SpecRefused, SV.PartRefused)):
            run(eng, decl, tmp_path / key)


def test_a_lever_outside_the_allowlist_refuses(eng, tmp_path, w42):
    """F-8: the note's plain side levers (direction, fade, invert_trigger, bias) and any lever without a searched id."""
    for name, values, lever in (("direction", ["-1", "1"], ""), ("fade", ["no", "yes"], ""),
                                ("invert_trigger", ["no", "yes"], "side"), ("bias", ["up", "down"], "A99")):
        extra = [{"name": name, "values": values, "lever": lever}]
        decl = declare(eng, tmp_path / name, w42, space={"extra": extra})
        with pytest.raises(SV.PartRefused, match="allowlist"):
            run(eng, decl, tmp_path / name / "out")


def test_the_spec_is_exactly_its_form(eng, tmp_path, w42):
    good = SV._block(declare(eng, tmp_path, w42).read_bytes())
    SV.load_spec(W.declaration(good))
    fi, pl = good["finalists"], good["plateau"]
    bad = [dict(baselines={"names": ["naive_coin"], "seed": 13}),
           dict(baselines={"names": ["naive_coin", "p14", "p15", "my_weak"], "seed": 13}),
           dict(finalists=dict(fi, reread_seeds=[300, 301, 302, 303])), dict(finalists=dict(fi, z=0)),
           dict(finalists=dict(fi, reread_seeds=[101, 300, 301, 302, 303])),
           dict(finalists=dict(fi, margin=0.1)),
           dict(plateau=dict(pl, rule=dict(pl["rule"], margin=0.1))),
           dict(plateau=dict(pl, rule=dict(pl["rule"], side="two_sided"))),
           dict(survey=dict(good["survey"], seed=11.5)), dict(prereg_id="RD-9"),
           dict(rounds={k: v for k, v in good["rounds"].items() if k != "kappa"}),
           dict(parts=dict(good["parts"], gate={k: v for k, v in good["parts"]["gate"].items() if k != "keys"}))]
    for over in bad:
        with pytest.raises(SV.SpecRefused):
            SV.load_spec(W.declaration({**good, **over}))
    with pytest.raises(SV.SpecRefused):
        SV.load_spec(W.declaration(good) + W.declaration(good))


@pytest.mark.parametrize("runner", [{"tag": "heldout_test"}, {"tag": "confirmation"},
                                    {"blocks": [["2022-01-03", "2024-06-28"]]}, {"horizon": 400}],
                         ids=["heldout-tag", "confirm-tag", "held-out-block", "held-out-horizon"])
def test_a_held_out_run_refuses_first(eng, tmp_path, w42, runner):
    """F-4: refused at the first run, before the book, the gate or any reading; the failure record and variants
    written, no readings."""
    with pytest.raises(eng.SS.HeldOutInput):
        survey(eng, tmp_path, w42, runner=dict(runner, kind="plateau"))
    out = tmp_path / "out"
    assert len(W.CALLS) == 1 and (out / "F-99_survey_failure.csv").is_file()
    assert not (out / "F-99_survey_readings.csv").exists() and rows_of(out / "variants.jsonl")


def test_a_held_out_protocol_refuses_before_any_cell(eng, tmp_path, w42):
    for i, pr in enumerate(({"blocks": [["2022-01-03", "2024-06-28"]]}, {"horizon": 1000})):
        with pytest.raises(eng.SS.HeldOutInput):
            survey(eng, tmp_path / str(i), w42, spec_over={"protocol": dict(W.SPEC["protocol"], **pr)})
        assert W.CALLS == [] and not (tmp_path / str(i) / "out").exists()


def test_a_held_out_variants_row_refuses_before_the_survey(eng, tmp_path, w42):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "variants.jsonl").write_text(json.dumps({"label": "heldout_test", "params": {}}) + "\n",
                                                     encoding="utf-8")
    with pytest.raises(SV.HeldOutRow):
        survey(eng, tmp_path, w42)
    assert W.CALLS == []
    assert SV.heldout_problems([{"label": "s", "params": {"day": "2024-01-02"}}])
    assert not SV.heldout_problems([{"label": "survey:proposed", "params": {"confirm_bars": 2, "judged_x": 1}}])


def test_a_second_run_refuses(eng, tmp_path, w42):
    """F-5: the same declaration again, into the same folder under another name, or under the same name."""
    decl = declare(eng, tmp_path, w42, "noise")
    run(eng, decl, tmp_path / "out")
    with pytest.raises(SV.RunRepeated, match="run once"):
        SV.run_survey(decl, results_dir=tmp_path / "out", name="F-99_again", pin_fixture=SV.fixture_pin(decl),
                      engine=eng, writer=local_writer, variants_writer=local_variants)
    with pytest.raises(SV.RunRepeated, match="never overwritten"):
        run(eng, decl, tmp_path / "out")


def test_a_refusal_after_the_first_cell_writes_variants_first(eng, tmp_path, w42):
    """m-4, F-6: a plateau rule leaving a lever unstepped refuses after every read; the variants rows are written
    first, and even when the failure record cannot be written."""
    rule = dict(W.SPEC["plateau"]["rule"], steps={"x": 0.1, "y": 2})
    ORDER.clear()
    with pytest.raises(eng.PL.PlateauRefused):
        survey(eng, tmp_path / "a", w42, spec_over={"plateau": dict(W.SPEC["plateau"], rule=rule)})
    out = tmp_path / "a" / "out"
    fail = csv(out / "F-99_survey_failure.csv")
    assert ORDER == ["variants", "F-99_survey_failure"]
    assert len(rows_of(out / "variants.jsonl")) == json.loads(fail["counts"][0])["cells"] > 0

    def broken(df, name, **kw):
        if name.endswith("_failure"):
            raise OSError("the disk is full")
        return local_writer(df, name, **kw)
    decl = declare(eng, tmp_path / "b", w42, spec_over={"plateau": dict(W.SPEC["plateau"], rule=rule)})
    with pytest.raises(eng.PL.PlateauRefused) as e:
        SV.run_survey(decl, results_dir=tmp_path / "b" / "out", name="F-99_survey",
                      pin_fixture=SV.fixture_pin(decl), engine=eng, writer=broken, variants_writer=local_variants)
    assert rows_of(tmp_path / "b" / "out" / "variants.jsonl")
    assert any("failure record could not be written" in n for n in getattr(e.value, "__notes__", []))


def test_a_dirty_tree_refuses_under_a_pin(eng, tmp_path, w42, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "prereg").mkdir(parents=True)
    (repo / "results").mkdir()
    inside = repo / "results" / "w42_r1.json"
    inside.write_bytes(Path(w42["file"]).read_bytes())
    mine = repo / "prereg" / "F-99_toy.md"
    mine.write_bytes(declare(eng, tmp_path, dict(w42, file=str(inside))).read_bytes())
    (repo / "DECISIONS.md").write_text(f"| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 "
                                       f"`{R.sha256_lf(mine)}` | t |\n", encoding="utf-8")
    monkeypatch.setattr(SV, "ROOT", repo)
    monkeypatch.setattr(SV.R, "_dirty", lambda tree: ["extended/survey.py"])
    with pytest.raises(SV.PartRefused, match="clean"):
        SV.run_survey(mine, results_dir=repo / "out", name="x")
    monkeypatch.setattr(SV.R, "_dirty", lambda tree: [])
    monkeypatch.setattr(SV.R, "_commit", lambda tree, what: "c" * 40)
    with pytest.raises(SV.PartRefused, match="extended"):          # a part outside extended. under a pin
        SV.run_survey(mine, results_dir=repo / "out", name="x")


def test_an_engine_without_q192_refuses(eng, tmp_path, w42, monkeypatch):
    monkeypatch.undo()
    with pytest.raises(SV.PartRefused, match="Q-192"):
        survey(eng, tmp_path, w42)
    assert W.CALLS == []


def test_the_engine_that_stood_is_required(eng):
    class Old:
        SS = type("SS", (), {"Sampler": type("S", (), {"survey": lambda self, n, *, ledger: None}),
                             "admit_one": staticmethod(lambda r, *, ledger, protocol: r),
                             "CellLedger": type("L", (), {"begin": lambda self, role, seed: None})})
    with pytest.raises(SV.PartRefused, match=SV.ENGINE_COMMIT):
        SV.Engine(Old.SS, eng.P, eng.PL).check()


# ------------------------------------------------------------------------------------------------ under a real pin


def test_a_real_pin_with_the_defaults_in_a_process_of_their_own(tmp_path):
    """A real pin (a scratch repository standing as `ROOT`: its own DECISIONS.md; its tree's clean state and commit
    stood in, `test_a_dirty_tree_refuses_under_a_pin` holds the refusal) with the default engine, `extended.results.write_result` and the vendored `VariantCounter`. The toy parts
    stand as `extended.survey_toy` (a copy of `tests/survey_world.py` on `extended.__path__`), since under a pin a part
    is `extended.`'s. Its own process: the vendored tree goes on sys.path."""
    code = textwrap.dedent(f"""
        import sys, json, shutil, subprocess
        from pathlib import Path
        sys.path.insert(0, {str(ROOT / 'tests')!r})
        import survey_world as W
        W.load_wave42()
        import extended
        tmp = Path({str(tmp_path)!r})
        toy = tmp / "toy"; toy.mkdir()
        shutil.copy({str(ROOT / 'tests' / 'survey_world.py')!r}, toy / "survey_toy.py")
        extended.__path__.append(str(toy))
        from extended import survey as SV
        from extended import reader as R
        E = SV.Engine.default()
        E.SS.CellLedger.protocol_for = W.q192_protocol_for(E.SS.CellLedger.protocol_for)
        repo = tmp / "repo"; (repo / "prereg").mkdir(parents=True); (repo / "results").mkdir()
        W.w42_fixture(repo / "results" / "w42_r1.json")
        obj = {{"rule_id": "W42-R1", "file": "results/w42_r1.json",
               "sha256": R.sha256_lf(repo / "results" / "w42_r1.json"), "code_sha256": SV.w42_code_sha()}}
        parts = {{k: dict(v, id=v["id"].replace("survey_world:", "extended.survey_toy:"))
                 for k, v in W.parts_of("plateau").items()}}
        decl = repo / "prereg" / "F-99_toy.md"
        decl.write_bytes(W.declaration(W.spec(SV.declare_parts(parts, E), obj)).encode())
        (repo / "DECISIONS.md").write_text("| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 `"
                                           + R.sha256_lf(decl) + "` | t |\\n", encoding="utf-8")
        SV.ROOT = repo
        SV.R._dirty = lambda tree: []                     # the scratch tree stands clean (no commit is made here)
        SV.R._commit = lambda tree, what: "c" * 40
        out = SV.run_survey(decl, results_dir=repo / "out", name="F-99_s")
        from extended.results import verify_result, read_manifest
        man = read_manifest(out.list_path)
        print(json.dumps({{"ok": [verify_result(p)[0] for p in (out.list_path, out.readings_path,
                                                                out.candidates_path)],
                           "row": out.pin_row, "finalists": len(out.finalists), "cells": out.counts["cells"],
                           "commit": len(str(man.parameters["commit"])),
                           "variants": len((repo / "out" / "variants.jsonl").read_text().splitlines())}}))
    """)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=600, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["ok"] == [True, True, True] and got["row"] == "E-999" and got["finalists"] >= 1
    assert got["variants"] == got["cells"] and got["commit"] == 40
