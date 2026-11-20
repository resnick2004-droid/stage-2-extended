"""Wave 5's survey runner (`extended/survey.py`), end to end on the synthetic worlds of `tests/survey_world.py` over
Wave 3.4's engine as it stood (df367a7). No bar, no result file of the repository: every output goes to a temporary
folder.

* the planted region is found within the declared budget; under pure noise, a near miss, a stronger baseline, a crossed
  limit, a harmful or coin-chosen side, a hedge across accounts, a refused gate or a spike, there is no finalist --
  each world checked to bite (the step it tests is what refuses);
* every cell is counted, the variants rows carry the declaration's and the protocol's sha256, and are written last;
* a second run with the same seeds is byte-identical; one ledger a run;
* the refusals: unpinned, a wrong fixture, a fixture under prereg/ or into results/, a pin outside this repository, a
  part that differs from its binding, a searched side lever, a spec off its form (m-1), a held-out reading, block,
  horizon or variants row; a refusal after the first cell writes its failure record and its variants rows (m-4);
* a mutation of each step is killed by the scenario's own verdict, an exception counting only when it is the
  expected refusal (S-2).
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

import pandas as pd
import pytest

from extended import ROOT
from extended import reader as R
from extended import survey as SV

import survey_world as W   # noqa: E402  (tests/ is on sys.path under pytest's rootdir)


@pytest.fixture(scope="module")
def eng():
    SS, SG, P, PL = W.engine()
    E = SV.Engine(SS, P, PL)
    E.check()
    return E


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


ORDER: list[str] = []


def make_parts(eng, world, **over):
    kw = dict(space=W.space(eng.SS), build_schedule=world.build_schedule, runner=world.runner, gate=world.gate,
              engine=eng, writer=local_writer, variants_writer=local_variants)
    kw.update(over)
    return SV.Parts(**kw)


def setup(eng, tmp: Path, kind="plateau", *, world=None, spec_over=None, bind_parts=None, **over):
    world = world or W.World(kind)
    parts = make_parts(eng, world, **over)
    s = W.spec(SV.bindings(bind_parts or parts, eng), **(spec_over or {}))
    (tmp / "decl").mkdir(parents=True, exist_ok=True)
    decl = tmp / "decl" / "F-99_decl.md"
    decl.write_bytes(W.declaration(s).encode("utf-8"))
    return decl, parts, world


def survey(eng, tmp: Path, kind="plateau", **kw):
    decl, parts, world = setup(eng, tmp, kind, **kw)
    out = SV.run_survey(decl, parts, results_dir=tmp / "out", name="F-99_survey", pin_fixture=SV.fixture_pin(decl))
    return out, world


def rows_of(p: Path) -> list[dict]:
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]


def csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p, dtype=str, keep_default_na=False)


def audit(out, world, spec=W.SPEC) -> list[str]:
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
    if not set(world.calls) <= cells:
        probs.append("the runner ran a design that is not a counted cell")
    if len(rows_of(out.variants_path)) != len(led.rows):
        probs.append("the variants rows are not the ledger's cells")
    if R.sha256_lf(out.list_path) != out.list_sha256:
        probs.append("the list sha is not the list file's")
    lst, reads = csv(out.list_path), csv(out.readings_path)
    rr = {(r["id"]): float(r["value"]) for _, r in reads.iterrows() if r["role"] == "reread" and r["value"]}
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
            if not all(g["z"] > spec["finalists"]["z"] for g in f["gaps"].values()) or \
                    set(f["gaps"]) != set(SV.BASELINES):
                probs.append(f"finalist {f['id']} does not beat each baseline")
            if not all(v["inside"] for v in f["limits"].values()) or not f["no_harm"]["held"] or \
                    not f["plateau"]["accepted"]:
                probs.append(f"finalist {f['id']} is outside a limit, the no-harm floor or a plateau")
    elif out.token is not None or len(lst):
        probs.append("no finalist, but a token or a list row")
    if len(lst) != len(out.finalists) or len(csv(out.candidates_path)) != len(out.candidates):
        probs.append("the list or the candidates file does not hold the run's")
    return probs


def in_region(design) -> bool:
    return W.bump(design) >= 0.5 * W.A


def reasons(out) -> str:
    return " | ".join(str(c.get("reason", "")) for c in out.candidates)


# ------------------------------------------------------------------------------------------------ the scenarios
# Each returns True when the survey behaves correctly in its world, and checks that the world bites.


def sc_planted(eng, tmp):
    out, world = survey(eng, tmp, "plateau")
    return bool(out.finalists) and all(in_region(f["design"]) for f in out.finalists) and audit(out, world) == []


def _none(kind, bite):
    def sc(eng, tmp):
        out, world = survey(eng, tmp, kind)
        return out.finalists == [] and audit(out, world) == [] and bite(out)
    return sc


def _spike_bites(out):
    hit = [c for c in out.candidates if abs(c["design"]["x"] - 0.3) < 1e-9]
    return any("plateau" in c for c in hit)


def _near_bites(out):     # some candidate's every gap is past the margin, yet not by z standard errors
    return any(c.get("gaps") and all(g["gap"] > W.SPEC["finalists"]["margin"] for g in c["gaps"].values())
               for c in out.candidates)


def _strong_bites(out):   # some candidate beats the naive coin but not P-16
    return any(c.get("gaps") and c["gaps"]["naive_coin"]["beaten"] and not c["gaps"]["p16"]["beaten"]
               for c in out.candidates)


def _refused_rows(cls):
    def bite(out):
        return any(r.startswith(cls) for r in csv(out.readings_path)["refused"])
    return bite


SCENARIOS = {
    "planted": sc_planted,
    "noise": _none("noise", lambda out: len(out.candidates) == W.SPEC["finalists"]["candidates"]),
    "spike": _none("spike", _spike_bites),
    "near": _none("near", _near_bites),
    "strong": _none("strong", _strong_bites),
    "limit": _none("limit", lambda out: "every limit inside" in reasons(out)),
    "harm": _none("harm", lambda out: "no-harm" in reasons(out)),
    "coin_side": _none("coin_side", lambda out: "no-harm" in reasons(out)),
    "hedge": _none("hedge", _refused_rows("tier1")),
    "gated": _none("gated", _refused_rows("gate")),
}


def sc_unpaired(eng, tmp):
    try:
        survey(eng, tmp, "unpaired")
    except SV.SurveyRefused as e:
        return "paired" in str(e)
    return False


def sc_heldout(eng, tmp, **world_kw):
    world = W.World("plateau", **(world_kw or {"tag": "heldout_test"}))
    try:
        survey(eng, tmp, world=world)
    except eng.SS.HeldOutInput:
        out = tmp / "out"
        return len(world.calls) == 1 and (out / "F-99_survey_failure.csv").is_file() and \
            not (out / "F-99_survey_readings.csv").exists() and not (out / "F-99_survey_finalists.csv").exists()
    return False


SCENARIOS.update(unpaired=sc_unpaired, heldout=sc_heldout)


def test_every_scenario_behaves_unmutated(eng, tmp_path):
    """The kill tests' control: each world, unmutated, gives the correct verdict and bites."""
    bad = [name for name, sc in SCENARIOS.items() if not sc(eng, tmp_path / name)]
    assert bad == []


# ------------------------------------------------------------------------------------------------ the mutations


def _with_spec(ctx, **kw):
    c = copy.copy(ctx)
    c.spec = dataclasses.replace(ctx.spec, **kw)
    return c


def _fixed_schedule(orig):
    def m(ctx, d, p, role):
        b = ctx.parts.build_schedule
        ctx.parts.build_schedule = lambda _d: b({"x": 0.0, "y": 0, "k": "a"})
        try:
            return orig(ctx, d, p, role)
        finally:
            ctx.parts.build_schedule = b
    return m


def _reread_from_selection(orig):
    def m(ctx):
        out = orig(ctx)
        for r in ctx.records:
            if "reread_value" in r:
                r["reread_value"] = r["selection_value"]
        return out
    return m


def _no_door(orig):
    def m(ctx, design, per, out, measure, reread, roles):
        import numpy as np
        per = np.asarray(per, float).ravel()
        return ctx.E.SS.Reading(dict(design), float(per.mean()), tuple(out.blocks), tuple(out.seeds), str(out.tag),
                                measure, out.horizon, 0.1, tuple(per))
    return m


_ACCEPT = type("V", (), dict(accepted=True, reason="mutant", rule="m", evaluated=0, held=0))

#: (the function of extended/survey.py mutated, how, the scenario that must catch it, the refusal it may raise)
MUTANTS = {
    "survey-seed": ("draw_survey", lambda o: (lambda ctx: ctx.E.SS.Sampler(
        ctx.parts.space, seed=ctx.spec.survey_seed + 1, method=ctx.spec.method).survey(
        ctx.spec.survey_n, ledger=ctx.ledger, protocol=ctx.protocol, reread_seeds=ctx.spec.reread_seeds,
        measures=("risk",), max_proposals=ctx.spec.max_proposals)), "planted", ()),
    "schedule-fixed": ("read_design", _fixed_schedule, "planted", ()),
    "reread-not-fresh": ("read_design", lambda o: (lambda ctx, d, p, role: o(ctx, d, ctx.protocol, role)), "planted",
                         ("OffProtocol",)),
    "composite-sign": ("composite_score", lambda o: (lambda dims: (lambda arm: -o(dims)(arm))), "planted", ()),
    "rounds-skipped": ("run_rounds", lambda o: (lambda ctx: None), "planted", ()),
    "order-reversed": ("finalist_candidates", lambda o: (lambda ctx: list(reversed(sorted(
        {r.id: r for r in ctx.readings}.values(), key=lambda r: (float(r.value), r.id))))[:ctx.spec.candidates]),
        "planted", ()),
    "baselines-ignored": ("beats_baselines", lambda o: (lambda ctx, got: (True, o(ctx, got)[1])), "noise", ()),
    "margin-ignored": ("beats_baselines", lambda o: (lambda ctx, got: o(_with_spec(ctx, margin=1e-12), got)), "near",
                       ()),
    "z-ignored": ("beats_baselines", lambda o: (lambda ctx, got: o(_with_spec(ctx, z=1e-12), got)), "near", ()),
    "first-baseline-only": ("beats_baselines", lambda o: (lambda ctx, got: o(_with_spec(
        ctx, baselines=ctx.spec.baselines[:1]), got)), "strong", ()),
    "limits-ignored": ("limits_inside", lambda o: (lambda ctx, sel: (True, o(ctx, sel)[1])), "limit", ()),
    "no-harm-skipped": ("no_harm", lambda o: (lambda ctx, out: (True, o(ctx, out)[1])), "harm", ()),
    "side-source-ignored": ("no_harm", lambda o: (lambda ctx, out: o(ctx, dataclasses.replace(
        out, side_source=SV.TRIGGER))), "coin_side", ()),
    "book-skipped": ("book_check", lambda o: (lambda out: None), "hedge", ()),
    "gate-skipped": ("gate_check", lambda o: (lambda ctx, out: None), "gated", ()),
    "plateau-skipped": ("plateau_step", lambda o: (lambda ctx, f: _ACCEPT()), "spike", ()),
    "check-output-dropped": ("_check_output", lambda o: (lambda ctx, out, p: None), "unpaired", ()),
    "reread-value-from-selection": ("choose_finalists", _reread_from_selection, "planted", ()),
    "list-sha-from-declaration": ("emit", lambda o: (lambda ctx, fin, **kw: {**o(ctx, fin, **kw),
                                                                            "list_sha256": ctx.sha}), "planted", ()),
    "door-skipped": ("_reading", _no_door, "heldout", ()),
}


def _killed(eng, tmp, scenario: str, expected: tuple[str, ...]) -> bool:
    """Killed: the scenario's verdict is wrong, or the expected refusal is raised -- never any other exception."""
    classes = tuple(getattr(eng.SS, n) for n in expected)
    try:
        return not SCENARIOS[scenario](eng, tmp)
    except classes or ():
        return True


@pytest.mark.parametrize("mutant", sorted(MUTANTS))
def test_a_mutation_of_each_step_is_killed(eng, tmp_path, monkeypatch, mutant):
    fn, how, scenario, expected = MUTANTS[mutant]
    monkeypatch.setattr(SV, fn, how(getattr(SV, fn)))
    assert _killed(eng, tmp_path, scenario, expected), f"the mutant {mutant} survived"


# ------------------------------------------------------------------------------------------------ counts and bytes


def test_every_cell_is_counted_and_carries_its_protocol(eng, tmp_path):
    ORDER.clear()
    out, world = survey(eng, tmp_path, "plateau")
    led = out.ledger
    vrows = rows_of(out.variants_path)
    assert len(vrows) == len(led.rows) == out.counts["cells"]
    assert [r["label"] for r in vrows] == [f"{r['role']}:{r['status']}" + (f":{r['class']}" if r["class"] else "")
                                           for r in led.rows]
    assert {r["params"]["_declaration_sha256"] for r in vrows} == {out.declaration_sha256}
    assert {r["params"]["_protocol_sha256"] for r in vrows} == {SV.protocol_digest(led.protocol)}
    roles = {r["role"] for r in led.rows}
    assert {"baseline", "survey", "round-1", "round-2"} <= roles and any(r.startswith("plateau:") for r in roles)
    assert sum(r["role"] == "baseline" for r in led.rows) == len(SV.BASELINES)
    cells = {r["id"] for r in led.rows if r["status"] == "proposed"}
    assert set(world.calls) <= cells and set(csv(out.readings_path)["id"]) <= cells
    man = json.loads((out.list_path.parent / (out.list_path.name + ".manifest.json")).read_text())
    assert man["variant_count"] == out.counts["cells"]
    assert man["parameters"]["bindings"] == out.bindings and man["parameters"]["pin_row"] == "fixture"
    assert ORDER == ["F-99_survey_readings", "F-99_survey_candidates", "F-99_survey_finalists", "variants"]
    assert audit(out, world) == []


def test_same_seeds_same_bytes(eng, tmp_path):
    a, _ = survey(eng, tmp_path / "a", "plateau")
    b, _ = survey(eng, tmp_path / "b", "plateau")
    for p, q in ((a.list_path, b.list_path), (a.readings_path, b.readings_path),
                 (a.candidates_path, b.candidates_path)):
        assert p.read_bytes() == q.read_bytes()
    assert a.token == b.token and rows_of(a.variants_path) == rows_of(b.variants_path)


def test_one_ledger_a_run(eng, tmp_path, monkeypatch):
    made = []
    init = eng.SS.CellLedger.__init__

    def counting(self, *a, **k):
        made.append(self)
        init(self, *a, **k)
    monkeypatch.setattr(eng.SS.CellLedger, "__init__", counting)
    out, _ = survey(eng, tmp_path, "noise")
    assert len(made) == 1 and made[0] is out.ledger


def test_the_limits_check_and_the_candidates_are_written(eng, tmp_path):
    out, _ = survey(eng, tmp_path, "plateau")
    lim = json.loads(csv(out.list_path)["limits"][0])["risk"]
    assert {"check_z", "check_level", "crossing_shown", "inside"} <= set(lim) and lim["inside"]
    cands = csv(out.candidates_path)
    assert list(cands["rank"]) == [str(i) for i in range(1, W.SPEC["finalists"]["candidates"] + 1)]
    assert all(cands["reason"])


# ------------------------------------------------------------------------------------------------ the refusals


def test_unpinned_and_bad_fixtures_refuse(eng, tmp_path):
    decl, parts, _ = setup(eng, tmp_path)
    for kw in ({}, {"pin_fixture": SV.FIXTURE_PREFIX + "0" * 64}):
        with pytest.raises(SV.NotPinned):
            SV.run_survey(decl, parts, results_dir=tmp_path / "out", name="x", **kw)
    with pytest.raises(SV.NotPinned):
        SV.run_survey(decl, parts, results_dir=tmp_path / "results", name="x", pin_fixture=SV.fixture_pin(decl))
    assert not (tmp_path / "out").exists()


def test_a_pin_comes_from_this_repository_only(eng, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "prereg").mkdir(parents=True)
    decl, parts, _ = setup(eng, tmp_path)
    mine = repo / "prereg" / "F-99_toy.md"
    mine.write_bytes(decl.read_bytes())
    (repo / "DECISIONS.md").write_text(f"| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 "
                                       f"`{R.sha256_lf(mine)}` | t |\n", encoding="utf-8")
    bare = dataclasses.replace(parts, engine=None, writer=None, variants_writer=None)
    with pytest.raises(SV.NotPinned, match="not a file of this repository"):     # another folder's log never pins
        SV.run_survey(mine, bare, results_dir=repo / "out", name="x")
    monkeypatch.setattr(SV, "ROOT", repo)
    with pytest.raises(SV.NotPinned, match="inside this repository"):
        SV.run_survey(mine, bare, results_dir=tmp_path / "elsewhere", name="x")
    with pytest.raises(SV.PartRefused, match="fixture pin"):                     # injected writers under a pin
        SV.run_survey(mine, parts, results_dir=repo / "out", name="x")
    with pytest.raises(SV.NotPinned, match="fixture pin never"):
        SV.run_survey(mine, parts, results_dir=tmp_path / "o2", name="x", pin_fixture=SV.fixture_pin(mine))
    mine.write_bytes(mine.read_bytes() + b"\nedited after the pin\n")
    with pytest.raises(SV.NotPinned, match="a change"):
        SV.run_survey(mine, bare, results_dir=repo / "out", name="x")


def test_a_part_that_differs_from_its_binding_refuses(eng, tmp_path):
    world = W.World("plateau")
    decl, parts, _ = setup(eng, tmp_path, world=world)
    other = W.World("noise")
    swaps = {"space": dict(space=W.space(eng.SS, x_hi=0.5)), "runner": dict(runner=other.runner),
             "gate": dict(gate=lambda out: None), "schedule_builder": dict(build_schedule=other.build_schedule)}
    for part, kw in swaps.items():
        with pytest.raises(SV.PartRefused, match=part):
            SV.run_survey(decl, dataclasses.replace(parts, **kw), results_dir=tmp_path / part, name="x",
                          pin_fixture=SV.fixture_pin(decl))
        assert not (tmp_path / part).exists()
    with pytest.raises(SV.PartRefused, match="gate is required"):
        SV.run_survey(decl, dataclasses.replace(parts, gate=None), results_dir=tmp_path / "g", name="x",
                      pin_fixture=SV.fixture_pin(decl))


def test_a_searched_side_lever_refuses(eng, tmp_path):
    for dim in (eng.SS.Dim("side", eng.SS.CAT, values=("long", "short")),
                eng.SS.Dim("entry", eng.SS.CAT, values=("buy", "sell"))):
        sp = W.space(eng.SS, extra=(dim,))
        decl, parts, _ = setup(eng, tmp_path / dim.name, space=sp)
        with pytest.raises(SV.PartRefused, match="side"):
            SV.run_survey(decl, parts, results_dir=tmp_path / dim.name / "out", name="x",
                          pin_fixture=SV.fixture_pin(decl))


def test_the_spec_is_exactly_its_form(eng, tmp_path):
    _, parts, _ = setup(eng, tmp_path)
    good = W.spec(SV.bindings(parts, eng))
    SV.load_spec(W.declaration(good))
    fi = good["finalists"]
    bad = [dict(baselines={"names": ["naive_coin"], "seed": 13}),
           dict(baselines={"names": ["naive_coin", "p14", "p15", "my_weak"], "seed": 13}),
           dict(finalists=dict(fi, reread_seeds=[300, 301, 302, 303])),
           dict(finalists=dict(fi, z=0)), dict(finalists=dict(fi, margin=0)),
           dict(finalists=dict(fi, reread_seeds=[101, 300, 301, 302, 303])),
           dict(survey=dict(good["survey"], seed=11.5)), dict(prereg_id="RD-9"),
           dict(rounds={k: v for k, v in good["rounds"].items() if k != "kappa"}),
           dict(parts=dict(good["parts"], gate={"id": "g"}))]
    for over in bad:
        with pytest.raises(SV.SpecRefused):
            SV.load_spec(W.declaration({**good, **over}))
    with pytest.raises(SV.SpecRefused):
        SV.load_spec(W.declaration(good) + W.declaration(good))
    with pytest.raises(SV.SpecRefused):
        SV.load_spec(W.declaration(good).replace('"horizon": 0', '"horizon": <h>'))


@pytest.mark.parametrize("world_kw", [{"tag": "heldout_test"}, {"tag": "confirmation"}],
                         ids=["heldout-tag", "confirm-tag"])
def test_a_held_out_reading_refuses_at_its_read(eng, tmp_path, world_kw):
    assert sc_heldout(eng, tmp_path, **world_kw)


def test_a_reported_held_out_block_or_horizon_refuses_at_its_read(eng, tmp_path):
    for i, kw in enumerate(({"blocks": [["2022-01-03", "2024-06-28"]]}, {"horizon": 400})):
        world = W.World("plateau", **kw)
        with pytest.raises((SV.SurveyRefused, eng.SS.HeldOutInput)):
            survey(eng, tmp_path / str(i), world=world)
        assert len(world.calls) == 1 and not (tmp_path / str(i) / "out" / "F-99_survey_readings.csv").exists()


def test_a_held_out_protocol_refuses_before_any_cell(eng, tmp_path):
    for i, pr in enumerate(({"blocks": [["2022-01-03", "2024-06-28"]]}, {"horizon": 1000})):
        world = W.World("plateau")
        with pytest.raises(eng.SS.HeldOutInput):
            survey(eng, tmp_path / str(i), world=world, spec_over={"protocol": dict(W.SPEC["protocol"], **pr)})
        assert world.calls == [] and not (tmp_path / str(i) / "out").exists()


def test_a_held_out_variants_row_refuses_before_the_survey(eng, tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "variants.jsonl").write_text(json.dumps({"label": "heldout_test", "params": {}}) + "\n",
                                                     encoding="utf-8")
    world = W.World("plateau")
    with pytest.raises(SV.HeldOutRow):
        survey(eng, tmp_path, world=world)
    assert world.calls == []
    assert SV.heldout_problems([{"label": "s", "params": {"day": "2024-01-02"}}])
    assert not SV.heldout_problems([{"label": "survey:proposed", "params": {"confirm_bars": 2, "judged_x": 1,
                                                                            "day": "2023-12-29"}}])


def test_a_refusal_after_the_first_cell_writes_its_record_and_variants(eng, tmp_path):
    """m-4: a plateau rule that leaves a lever unstepped refuses inside the finalists' step, after every read."""
    rule = dict(W.SPEC["plateau"]["rule"], steps={"x": 0.1, "y": 2})
    ORDER.clear()
    with pytest.raises(eng.PL.PlateauRefused):
        survey(eng, tmp_path, "plateau", spec_over={"plateau": dict(W.SPEC["plateau"], rule=rule)})
    out = tmp_path / "out"
    fail = csv(out / "F-99_survey_failure.csv")
    assert fail["exception"][0] == "PlateauRefused" and json.loads(fail["counts"][0])["cells"] > 0
    assert len(rows_of(out / "variants.jsonl")) == json.loads(fail["counts"][0])["cells"]
    assert ORDER == ["F-99_survey_failure", "variants"]


def test_the_engine_that_stood_is_required(eng):
    class Old:
        SS = type("SS", (), {"Sampler": type("S", (), {"survey": lambda self, n, *, ledger: None}),
                             "admit_one": staticmethod(lambda r, *, ledger, protocol: r),
                             "CellLedger": type("L", (), {"begin": lambda self, role, seed: None})})
    with pytest.raises(SV.PartRefused, match=SV.ENGINE_COMMIT):
        SV.Engine(Old.SS, eng.P, eng.PL).check()


# ------------------------------------------------------------------------------------------------ the defaults


def test_the_defaults_under_a_pin_in_a_process_of_their_own(tmp_path):
    """A real pin (this repository's log, `ROOT` pointed at a scratch repository) with the default engine,
    `extended.results.write_result` and the vendored `VariantCounter`: the vendored tree goes on sys.path, so this
    runs in its own process."""
    code = textwrap.dedent(f"""
        import sys, json
        sys.path.insert(0, {str(ROOT / 'tests')!r})
        from pathlib import Path
        import survey_world as W
        from extended import survey as SV
        from extended import reader as R
        repo = Path({str(tmp_path)!r}) / "repo"
        (repo / "prereg").mkdir(parents=True)
        SS = W.engine()[0]
        world = W.World("plateau")
        parts = SV.Parts(space=W.space(SS), build_schedule=world.build_schedule, runner=world.runner, gate=world.gate)
        decl = repo / "prereg" / "F-99_toy.md"
        decl.write_bytes(W.declaration(W.spec(SV.bindings(parts))).encode())
        (repo / "DECISIONS.md").write_text("| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 `"
                                           + R.sha256_lf(decl) + "` | t |\\n", encoding="utf-8")
        SV.ROOT = repo
        out = SV.run_survey(decl, parts, results_dir=repo / "out", name="F-99_s")
        from extended.results import verify_result
        print(json.dumps({{"ok": [verify_result(p)[0] for p in (out.list_path, out.readings_path,
                                                                out.candidates_path)],
                           "row": out.pin_row, "finalists": len(out.finalists), "cells": out.counts["cells"],
                           "variants": len((repo / "out" / "variants.jsonl").read_text().splitlines())}}))
    """)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=600, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    assert got["ok"] == [True, True, True] and got["row"] == "E-999" and got["finalists"] >= 1
    assert got["variants"] == got["cells"]
