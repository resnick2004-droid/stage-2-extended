"""Wave 5's survey runner (`extended/survey.py`), build v3, end to end on the synthetic worlds of
`tests/survey_world.py`: Wave 3.4's engine with Q-192, Q-192b and rm3-b (wt/wt-features 3452952), W42-R1 as it
stands (01e896a: its module, public scoring functions and DO_NOTHING_EPS, its application script, its real output file made by
`wave42_apply.apply`), Q-197's calendar loader (master 990d874). No bar, no result file of the repository, no held-out
calendar: every input and output is in a temporary folder (`SV.ROOT` pointed there).

* W42-R1's public functions reproduce its own `setting_rule` outputs on its H4 reading (the identity);
* the planted region is found within budget; in every other world there is no finalist, each world checked to bite;
* every cell is counted (through Q-192's pens), the bytes repeat, one ledger a run;
* the refusals (pins, rows, bindings, data, the space's digest, the allowlist, the spec's form, held-out first, the
  calendar, the runner's values, a second run, the engine, W42-R1's public functions, an unset limit, the process
  under a pin);
* M-2's do-nothing floor at 10, 11, 25 and 43 seeds, decided by W42-R1's `above_floor` (Q-186 m-1);
* Q-186's pre-pin fixes: data through the licensed data's junctions only, and the runner's data report equal to the
  declared (M-1, a real `mklink /J` junction on synthetic files); the rows' numbers with boundaries (m-2); the values'
  provenance under a pin (m-3); the driver and the entry script bound, the invocation exact (m-4); the once-record
  outside the checkout (m-5); a fixture run's token read by no held-out rule (m-6); the seven guards the red team's
  mutants passed (m-7);
* a mutation of each step is killed by its scenario's own verdict, an exception counting only when it is the expected
  refusal -- hand-written mutants and one-line source edits (`_edit`, the red team's mutplugin form).

The seeds here are small literals of these tests' own; none is a declared block.
"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import inspect
import json
import os
import subprocess
import sys
import textwrap
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

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
        row = f"| E-999 | 2026-11-20 | {out.token} -- the finalists |"
        if not str(out.token).startswith(SV.FIXTURE_TOKEN + " ") or R.HELDOUT_TOKENS["finalists"].match(row) or \
                R.heldout_tokens(row, "finalists") or R.HELDOUT_TOKEN_LIKE.search(str(out.token)):
            probs.append("a fixture run's token is in a form a held-out rule reads (m-6)")
        real = SV.finalists_token(spec["prereg_id"], out.declaration_sha256, out.list_sha256, fixture=False)
        m = R.HELDOUT_TOKENS["finalists"].match(f"| E-999 | 2026-11-20 | {real} -- the finalists |")
        if not m or m.group("sha") != out.declaration_sha256 or m.group("list") != out.list_sha256 \
                or m.group("decl") != spec["prereg_id"]:
            probs.append("the pinned form of the token is not Q-158's for this declaration and list")
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


# ------------------------------------------------------------------------------------------------ Q-186's scenarios
# Each returns True when the guard behaves correctly, and checks a control that it does not refuse everything.


def sc_floor_agrees(eng, tmp, roots):
    """m-1: the survey's do-nothing floor is W42-R1's `above_floor`, decision for decision, on p1_floor's band (per-seed
    values within a few ulps of floor + DO_NOTHING_EPS), where an exact-Fraction comparator disagrees with it."""
    ctx = SimpleNamespace(W=W42)
    with at(roots["default"]["root"]):
        base = SV.load_objective(W42)
    rng = np.random.default_rng(20261121)                    # this test's own seed
    agree, frac_differs = True, 0
    for floor in (1 / 6 + 1 / 6, base.floor):
        ctx.obj = dataclasses.replace(base, floor=floor)
        thr = float(floor) + W42.DO_NOTHING_EPS
        for n in (4, 10, 11, 25, 32, 43):
            for _ in range(400):
                per = thr + rng.integers(-3, 4) * np.spacing(thr) + rng.integers(-4, 5, size=n) * np.spacing(thr)
                r = SimpleNamespace(per_seed=tuple(-per), value=float(np.mean(-per)))
                got = SV.do_nothing_floor(ctx, r)[0]
                agree = agree and got == W42.above_floor(float(np.mean(per)), floor)
                exact = sum(Fraction(float(x)) for x in per) / n > Fraction(floor) + Fraction(W42.DO_NOTHING_EPS)
                frac_differs += exact != got
    return agree and frac_differs > 0


def sc_blocks(eng, tmp, roots):
    """m-7 `blocks`: a start on the calendar but in a gap between the protocol's blocks refuses; one inside does not."""
    cal = W.CAL
    i = next(k for k, d in enumerate(cal) if d >= "2022-01-01")
    ctx = SimpleNamespace(_pos={}, calendar=cal, protocol=SimpleNamespace(blocks=((cal[0], cal[i - 1]),
                                                                                  (cal[i + 1], cal[-1]))),
                          cal=SimpleNamespace(sessions_left=lambda d: len(cal) - cal.index(d)))
    ok = list(SV.sessions_left(ctx, [cal[0], cal[i + 1]])) == [len(cal), len(cal) - i - 1]
    try:
        SV.sessions_left(ctx, [cal[0], cal[i]])
    except SV.SurveyRefused as e:
        return ok and "outside the protocol's blocks" in str(e)
    return False


def _rows_root(tmp: Path, text: str) -> Path:
    root = tmp / "rows"
    root.mkdir(parents=True, exist_ok=True)
    (root / "DECISIONS.md").write_text(text, encoding="utf-8")
    return root


def _refuses(fn, cls, word) -> bool:
    try:
        fn()
    except cls as e:
        return word in str(e)
    return False


def sc_row_order(eng, tmp, roots):
    """m-7 `order`: under a real pin row, the margin's and the values' rows come before it (through `check_rows`)."""
    vsha = "ab" * 32
    vrow = f"W42-R1's values `results/w42_r1_values.csv` sha256 `{vsha}`"
    root = _rows_root(tmp, f"| E-099 | 2026-11-20 | {vrow} | t |\n| E-100 | 2026-11-20 | the no-harm margin is 0.005 | t |\n"
                           f"| E-102 | 2026-11-20 | {vrow} again | t |\n"
                           "| E-103 | 2026-11-20 | the no-harm margin is 0.005 again | t |\n")

    def spec(m, v):
        return SimpleNamespace(margin_row=m, no_harm_margin=0.005, values_row=v)
    with at(root):
        SV.check_rows(spec("E-100", "E-099"), "E-101", vsha, False)                     # the control
        return all(_refuses(lambda a=a: SV.check_rows(spec(*a), "E-101", vsha, False), SV.NotPinned,
                            "does not come before") for a in (("E-103", "E-099"), ("E-100", "E-102")))


def sc_margin_exact(eng, tmp, roots):
    """m-2: the margin's row names the no-harm margin and carries its number with numeric boundaries (p2_rows's three
    rows refuse, and a row without the margin's name); the values' row names W42-R1 and its file and carries the
    whole sha256. Each correct row passes."""
    vsha = "cd" * 32
    good_v = f"W42-R1's values `results/w42_r1_values.csv` sha256 `{vsha}`"
    cases = [("the no-harm margin is 0.0055", 0.005, False), ("delta floor 0.05; no-harm margin 0.02", 0.0, False),
             ("E-41 set the stop at 10.005 points", 0.005, False), ("the stop is 0.005 points", 0.005, False),
             ("the no-harm margin is 0.005 composite units", 0.005, True), ("the no-harm margin 0.0 (O-4)", 0.0, True)]
    vcases = [(good_v, True), (good_v.replace("W42-R1's", "the rule's"), False),
              (good_v.replace("w42_r1_values.csv", "values.csv"), False), (good_v.replace(vsha, vsha + "e"), False),
              (good_v.replace(vsha, "0" * 64), False)]
    ok = True
    for text, margin, want in cases:
        root = _rows_root(tmp / f"m{len(text)}{margin}", f"| E-100 | 2026-11-21 | {text} | t |\n")
        with at(root):
            spec = SimpleNamespace(margin_row="E-100", no_harm_margin=margin, values_row="fixture")
            got = not _refuses(lambda: SV.check_rows(spec, "fixture", vsha, True), SV.NotPinned, "does not carry")
        ok = ok and got == want
    for text, want in vcases:
        root = _rows_root(tmp / f"v{len(text)}{want}", f"| E-101 | 2026-11-21 | {text} | t |\n")
        with at(root):
            spec = SimpleNamespace(margin_row="fixture", no_harm_margin=0.005, values_row="E-101")
            got = not _refuses(lambda: SV.check_rows(spec, "fixture", vsha, True), SV.NotPinned, "does not carry")
        ok = ok and got == want
    return ok


def sc_caldigest(eng, tmp, roots):
    """m-7 `caldigest`: a calendar whose digest is not the one W42-R1's values were set on refuses."""
    r = roots["default"]
    with at(r["root"]):
        SV.load_calendar(W42, r["values"])                                               # the control
        bad = dict(r["values"], h4=dict(r["values"]["h4"], calendar_sha256="0" * 64))
        return _refuses(lambda: SV.load_calendar(W42, bad), SV.SpecRefused, "were set on")


def sc_paid(eng, tmp, roots):
    """m-7 `paid`: a unit paid (first payout within W) before its first pass refuses; a world's arm does not."""
    sl = np.array(W.STARTS_LEFT)
    arm = W.unit_values("paid", 1.0, (1, 2, 3, 4), len(sl))
    ctx = SimpleNamespace(W=W42)
    SV.validate_values(ctx, "design", arm, sl)                                          # the control
    bad = dict(arm, first_pass_days=np.full_like(arm["first_pass_days"], 20.0),
               first_payout_days=np.full_like(arm["first_payout_days"], 10.0))
    return 10.0 < 20.0 <= W42.W and _refuses(lambda: SV.validate_values(ctx, "design", bad, sl), SV.SurveyRefused,
                                             "paid before its first pass")


def _git_tmp(repo: Path, *args: str) -> None:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr


def sc_untracked(eng, tmp, roots):
    """m-7 `untracked`: `tree_problems` itself, on a temporary git repository (no commit made): an untracked
    `extended/x.py` and a staged file count; a git-ignored file does not."""
    repo = tmp / "git"
    (repo / "extended").mkdir(parents=True, exist_ok=True)
    _git_tmp(repo, "init", "-q")
    (repo / ".git" / "info").mkdir(parents=True, exist_ok=True)
    (repo / ".git" / "info" / "exclude").write_text("ignored/\n", encoding="utf-8")
    (repo / "ignored").mkdir(exist_ok=True)
    (repo / "ignored" / "y.txt").write_text("y\n", encoding="utf-8")
    (repo / "extended" / "a.py").write_text("A = 1\n", encoding="utf-8")
    _git_tmp(repo, "add", "extended/a.py")
    (repo / "extended" / "x.py").write_text("X = 1\n", encoding="utf-8")
    with at(repo):
        return sorted(SV.tree_problems()) == ["extended/a.py", "extended/x.py"]


def sc_offproto(eng, tmp, roots):
    """m-7 `offproto`: a runner reporting seeds other than its protocol's -- [101, 102, 103, 105], none held-out, so
    `_held_out_first` passes it -- refuses as off the protocol."""
    try:
        survey(eng, tmp, roots, runner={"kind": "plateau", "report_seeds": [101, 102, 103, 105]})
    except Exception as e:                                  # only the survey's own refusal counts
        return isinstance(e, SV.SurveyRefused) and "off the protocol" in str(e) and len(W.CALLS) == 1
    return False


def sc_check_level(eng, tmp, roots):
    """m-7 `checklevel`, n-1: the crossing check beside each limit is W42-R1's `limit_check` at the values'
    `check_level` (normal z), read back from every candidate's record."""
    from scipy import stats
    out = survey(eng, tmp, roots, "plateau")
    level = float(roots["default"]["values"]["limits"]["check_level"])
    z = float(stats.norm.ppf(1.0 - level))
    recs = [c["limits"] for c in out.candidates if c.get("limits")]
    return bool(recs) and audit(out) == [] and all(
        x["check_level"] == level and x["check_z"] == z and x["crossing_shown"] == (x["check_beyond"] > z * x["check_se"])
        and x["check_beyond"] == ((x["value"] - x["bound"]) if x["direction"] == "<=" else (x["bound"] - x["value"]))
        for lims in recs for x in lims.values())


def _junction(link: Path, target: Path) -> bool:
    """A real directory junction (`mklink /J`) to synthetic files in a temporary folder; False where none can be
    made."""
    if os.name != "nt":
        return False
    link.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, text=True,
                       timeout=60)
    return r.returncode == 0 and os.path.isjunction(link)


def _unlink(links) -> None:
    for link in links:                                      # the link only, never through it
        if os.path.isjunction(link) or os.path.islink(link):
            os.rmdir(link) if os.path.isjunction(link) else os.unlink(link)


def sc_data_junction(eng, tmp, roots):
    """M-1: in a temporary root, the licensed data's two junctions (`vendor/stage2/data/bars`, `data/atlas`, made by
    `mklink /J` to synthetic files outside the root) are inside it and `check_data` binds a file through them; a
    junction anywhere else (`results/foreign`, or `data` itself above `data/atlas`) refuses, as do `..` and absolute
    paths. `Path.resolve()` alone would have refused the bars (the red team's finding)."""
    root, root2, lic = tmp / "jroot", tmp / "jroot2", tmp / "licensed"
    for sub, body in (("bars/nq.parquet", b"synthetic bars\n"), ("atlas/a.csv", b"synthetic atlas\n"),
                      ("other/x.csv", b"x\n"), ("whole/atlas/a.csv", b"synthetic atlas\n")):
        (lic / sub).parent.mkdir(parents=True, exist_ok=True)
        (lic / sub).write_bytes(body)
    links = [(root / "vendor/stage2/data/bars", lic / "bars"), (root / "data/atlas", lic / "atlas"),
             (root / "results/foreign", lic / "other"), (root2 / "data", lic / "whole")]
    try:
        if not all(_junction(a, b) for a, b in links):
            return False
        P = SV.data_path_problem
        bars, atlas = "vendor/stage2/data/bars/nq.parquet", "data/atlas/a.csv"
        ok = P(bars, root) is None and P(atlas, root) is None and not SV._inside(root / bars, root)
        ok = ok and "results/foreign" in str(P("results/foreign/x.csv", root)) and "link data" in str(P(atlas, root2))
        ok = ok and all(P(x, root) is not None for x in ("../licensed/bars/nq.parquet", str(lic / "bars/nq.parquet"),
                                                         "vendor\\stage2\\data\\bars\\nq.parquet", "./data/atlas/a.csv"))

        def spec(data):
            return SimpleNamespace(parts={k: {"data": data if k == "runner" else {}} for k in SV.PART_NAMES})
        with at(root):
            ok = ok and not _refuses(lambda: SV.check_data(spec({bars: SV._raw_sha(root / bars),          # bound
                                                                  atlas: SV._raw_sha(root / atlas)})),
                                     SV.PartRefused, "")
            ok = ok and _refuses(lambda: SV.check_data(spec({bars: "0" * 64})), SV.PartRefused, "declared sha256")
            ok = ok and _refuses(lambda: SV.check_data(spec({"results/foreign/x.csv": SV._raw_sha(lic / "other/x.csv")})),
                                 SV.PartRefused, "link")
        return ok
    finally:
        _unlink([a for a, _ in links])


def sc_data_report(eng, tmp, roots):
    """M-1: the runner's data report equals the declared data key for key -- a declared file it does not report
    refuses, and so does a report of another sha256 (the extra key is the `data` world)."""
    root = roots["default"]["root"]
    f = root / "results" / "toy_report.csv"
    f.write_bytes(b"a\n1\n")
    rel = "results/toy_report.csv"
    ok = True
    for i, (report, word) in enumerate(((None, "did not report declared data"), ({rel: "1" * 64}, "does not bind"))):
        parts = W.parts_of(runner={"kind": "plateau", **({"report_data": report} if report else {})})
        parts["runner"]["data"] = {rel: SV._raw_sha(f)}
        decl = declare(eng, tmp / f"r{i}", parts=parts)
        try:
            run(eng, root, decl, tmp / f"r{i}" / "out")
            ok = False
        except Exception as e:                              # only the survey's own refusal counts
            ok = ok and isinstance(e, SV.SurveyRefused) and word in str(e) and len(W.CALLS) == 1
    return ok


def sc_provenance(eng, tmp, roots):
    """m-3: under a pin the values file is a pinned application -- each refusal on its own (pinned_commit not 40 hex,
    git_commit `-dirty` or not a commit, W42-R1's own commit rule refusing, `verify_result` failing), the rule called
    with (pinned_commit, head=git_commit); and W42-R1's real `commit_problem` on this repository's history."""
    pin, head = "b" * 40, "a" * 40
    calls = []

    class Rule:
        @staticmethod
        def commit_problem(repo, p, head=None):
            calls.append((p, head))
            return None if head == "a" * 40 else "not the pinned commit"

    def P(man, verify=lambda q: (True, "verified"), apply=Rule, repo=tmp):
        return " | ".join(SV.values_provenance_problems(man, tmp / "v.csv", repo=repo, apply=apply, verify=verify))

    def man(p=pin, h=head):
        return {"git_commit": h, "parameters": {"pinned_commit": p}}
    ok = P(man()) == "" and calls[-1] == (pin, head)
    ok = ok and "pinned_commit" in P(man(p=None)) and "pinned_commit" in P(man(p="b" * 39))
    ok = ok and "-dirty" in P(man(h=head + "-dirty")) and "not a commit" in P(man(h="fixture"))
    ok = ok and "commit rule" in P(man(h="c" * 40))
    ok = ok and "verify_result" in P(man(), verify=lambda q: (False, "modified since it was written"))
    git = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD", "HEAD~1"], capture_output=True, text=True)
    now, before = git.stdout.split()
    ok = ok and P(man(p=now, h=now), apply=APPLY, repo=REPO) == ""
    return ok and "not the pinned commit" in P(man(p=now, h=before), apply=APPLY, repo=REPO)


def sc_invocation(eng, tmp, roots):
    """m-4: the pinned invocation is exactly `python scripts/survey_run.py <declaration>`; `-c` (a runpy wrapper),
    `-m`, `-i`, `-X`, another script or declaration, the interactive and inspect flags and PYTHONSTARTUP,
    PYTHONINSPECT or PYTHONPATH each refuse (synthetic argv, flags and environment)."""
    root = tmp / "inv"
    decl = root / "prereg" / "F-99_x.md"
    script, rel = str(root / SV.ENTRY_SCRIPT), "prereg/F-99_x.md"
    calm = SimpleNamespace(interactive=0, inspect=0)

    def P(argv, flags=calm, env=None):
        return SV.invocation_problems(root, decl, argv=argv, flags=flags, env=env or {"PATH": "x"})
    bad = [["python", "-c", "import runpy; runpy.run_path('scripts/survey_run.py', run_name='__main__')"],
           ["python", "-X", "utf8", script, rel], ["python", "-i", script, rel], ["python", "-m", "survey_run", rel],
           ["python", str(root / "scripts" / "other.py"), rel], ["python", script, "prereg/F-98_y.md"],
           ["python", script], ["python", script, rel, "extra"], ["python", script, "-v"]]
    return P(["python", script, rel]) == [] and all(P(a) for a in bad) and \
        P(["python", script, rel], flags=SimpleNamespace(interactive=1, inspect=0)) and \
        P(["python", script, rel], flags=SimpleNamespace(interactive=0, inspect=1)) and \
        all(P(["python", script, rel], env={k: "1"}) == [f"{k} is set"] for k in SV.INVOCATION_ENV)


def sc_driver_bound(eng, tmp, roots):
    """m-4: `objective.code_sha256` binds the driver's own closure (`extended.survey`, `extended.results`,
    `extended.reader`) and the entry script; a run whose entry script differs from the declared one (a synthetic
    script stood in) refuses at the binding, before any cell."""
    oc = SV.objective_code()
    ok = {"extended.survey", "extended.results", "extended.reader"} <= set(oc["driver"]) and \
        oc[SV.ENTRY_SCRIPT] == R.sha256_lf(REPO / SV.ENTRY_SCRIPT) and SV.W42_SCRIPT in oc
    decl = declare(eng, tmp)
    fake = tmp / "fake" / SV.ENTRY_SCRIPT
    fake.parent.mkdir(parents=True, exist_ok=True)
    fake.write_bytes((REPO / SV.ENTRY_SCRIPT).read_bytes() + b"\n# an edit after the pin\n")
    real = SV.entry_file
    SV.entry_file = lambda: fake
    try:
        return ok and _refuses(lambda: run(eng, roots["default"]["root"], decl, tmp / "out"), SV.PartRefused,
                               "objective_code") and W.CALLS == []
    finally:
        SV.entry_file = real


def sc_once(eng, tmp, roots):
    """m-5: the once-record (injected under a fixture pin): a run appends one line before its first cell, even when it
    then refuses; a second run of the declaration from a fresh folder refuses before any cell and appends nothing; a
    damaged record refuses; another declaration passes; a record inside the checkout is refused; the default lies in
    the runs folder, outside every checkout."""
    root = roots["default"]["root"]
    once = tmp / "runs" / "survey_once.jsonl"
    decl = declare(eng, tmp, "noise")
    out = run(eng, root, decl, tmp / "o1", once_file=once)
    first = once.read_text(encoding="utf-8").splitlines()
    if not (len(first) == 1 and json.loads(first[0])["declaration_sha256"] == out.declaration_sha256):
        return False                                            # nothing recorded: the rest cannot be read
    ok = _refuses(lambda: run(eng, root, decl, tmp / "o2", once_file=once), SV.RunRepeated, "once-record")
    ok = ok and W.CALLS == [] and once.read_text(encoding="utf-8").splitlines() == first
    held = tmp / "runs" / "held.jsonl"                         # recorded before the first cell: a refusal counts too
    try:
        run(eng, root, declare(eng, tmp / "h", runner={"kind": "plateau", "tag": "heldout_test"}), tmp / "h" / "out",
            once_file=held)
        ok = False
    except eng.SS.HeldOutInput:
        ok = ok and len(held.read_text(encoding="utf-8").splitlines()) == 1
    SV.check_once_record("e" * 64, once)                        # another declaration
    damaged = tmp / "runs" / "damaged.jsonl"
    damaged.write_text(first[0] + "\n{not json\n", encoding="utf-8")
    ok = ok and _refuses(lambda: SV.check_once_record("e" * 64, damaged), SV.RunRepeated, "not JSON")
    ok = ok and SV.once_location_problem(REPO / "results" / "survey_once.jsonl", REPO) is not None
    ok = ok and SV.once_location_problem(SV.ONCE_FILE, REPO) is None and SV.ONCE_FILE.parent == Path(SV.RUNS_DIR)
    return ok


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
    "nothing": sc_nothing,
    "meagre": sc_meagre,
    "unpaid": sc_unpaid,
    "mixed": sc_mixed,
    "do_nothing_exact": sc_do_nothing_exact,
    "b5": sc_b5,
    "floor_agrees": sc_floor_agrees,
    "blocks": sc_blocks,
    "row_order": sc_row_order,
    "margin_exact": sc_margin_exact,
    "caldigest": sc_caldigest,
    "paid": sc_paid,
    "untracked": sc_untracked,
    "offproto": sc_offproto,
    "check_level": sc_check_level,
    "data_junction": sc_data_junction,
    "data_report": sc_data_report,
    "provenance": sc_provenance,
    "invocation": sc_invocation,
    "driver_bound": sc_driver_bound,
    "once": sc_once,
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


def _eps_dropped(orig):
    def m(ctx, r):
        c = -float(r.value)
        return c > ctx.obj.floor, {"do_nothing": {"composite": c, "floor": ctx.obj.floor, "held": c > ctx.obj.floor}}
    return m


def _fraction_floor(orig):
    """v3's own comparator (the red team's m-1): an exact mean against floor + eps, not W42-R1's `above_floor`."""
    def m(ctx, r):
        c = -sum(Fraction(float(x)) for x in r.per_seed) / len(r.per_seed)
        ok = c > Fraction(ctx.obj.floor) + Fraction(float(ctx.W.DO_NOTHING_EPS))
        return ok, {"do_nothing": {"composite": float(c), "floor": ctx.obj.floor, "held": ok}}
    return m


def _edit(fn_name: str, old: str, new: str):
    """A one-line source edit of `extended.survey`'s `fn_name`, compiled with the module's own globals (the red team's
    mutplugin form): the mutant is the function with `old` replaced by `new`, exactly once."""
    def make(orig):
        src = textwrap.dedent(inspect.getsource(orig))
        assert src.count(old) == 1, (fn_name, old)
        ns: dict = {}
        exec(compile("from __future__ import annotations\n" + src.replace(old, new), SV.__file__, "exec"),
             SV.__dict__, ns)
        return ns[fn_name]
    return make


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
        dict(x, direction="<=") for x in ctx.obj.limits)), rr, sel)), "floor", ("LimitDisagrees",)),
    "limits-from-selection": (SV, "limits_inside", lambda o: (lambda ctx, rr, sel: o(ctx, {**rr, **sel}, sel)),
                              "risky", ()),
    # n-1: these three are now caught earlier, by W42-R1's own limit_check disagreeing with the survey's reading
    "limit-as-mean": (SV, "limit_value", _limit_as_mean, "tail", ("LimitDisagrees",)),
    "limit-horizon-ignored": (SV, "limit_value", lambda o: (lambda ctx, arm, sl, lim: o(
        ctx, arm, np.full(len(sl), len(ctx.calendar)), lim)), "censor", ("LimitDisagrees",)),
    "sessions-left-overstated": (SV, "sessions_left", _ALL_COMPLETE, "censor", ()),
    "calendar-unchecked": (SV, "sessions_left", lambda o: (lambda ctx, starts: np.array(
        [len(ctx.calendar) - ctx.calendar.index(d) if d in ctx.calendar else len(ctx.calendar) for d in starts])),
        "offcal", ()),
    "values-unchecked": (SV, "validate_values", lambda o: (lambda ctx, name, arm, sl: None), "range", ()),
    "crossing-level-ignored": (SV, "limits_inside", lambda o: (lambda ctx, rr, sel: o(_with(ctx, check_level=0.5), rr,
                                                                                      sel)), "check_level", ()),
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
    "do-nothing-eps-dropped": (SV, "do_nothing_floor", _eps_dropped, "do_nothing_exact", ()),
    "do-nothing-by-fraction": (SV, "do_nothing_floor", _fraction_floor, "floor_agrees", ()),
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
    # Q-186 m-7: the seven the red team's mutplugin left alive, as its one-line edits
    "blocks": (SV, "sessions_left", _edit("sessions_left", "out = [d for d in s if not any(b0 <= d <= b1 for b0, b1 in "
                                          "ctx.protocol.blocks)]", "out = []"), "blocks", ()),
    "order": (SV, "check_rows", _edit("check_rows", "if pin_n is not None and int(rid[2:]) >= pin_n:", "if False:"),
              "row_order", ()),
    "caldigest": (SV, "load_calendar", _edit("load_calendar", 'if W.calendar_digest(dates) != values["h4"]'
                                             '["calendar_sha256"]:', "if False:"), "caldigest", ()),
    "paid": (SV, "validate_values", _edit("validate_values", "if (first[paid] > payout[paid]).any():", "if False:"),
             "paid", ()),
    "untracked": (SV, "tree_problems", _edit("tree_problems", '"--untracked-files=all"', '"--untracked-files=no"'),
                  "untracked", ()),
    "offproto": (SV, "_check_output", _edit("_check_output", "if tuple(out.seeds) != tuple(protocol.seeds)",
                                            "if False and tuple(out.seeds) != tuple(protocol.seeds)"), "offproto", ()),
    "checklevel": (SV, "limits_inside", _edit("limits_inside", 'lim["name"], b, ctx.obj.check_level)',
                                              'lim["name"], b, 0.5)'), "check_level", ()),
    # Q-186 M-1, m-2 to m-6: each new guard's own mutant
    "data-resolved": (SV, "data_path_problem", _edit("data_path_problem", "if not _lexically_inside(root / rel, root):",
                                                     "if not _inside(root / rel, root):"), "data_junction", ()),
    "data-any-link": (SV, "data_path_problem", _edit("data_path_problem", "if _is_link(root / sub) and sub not in "
                                                     "DATA_LINKS:", "if False:"), "data_junction", ()),
    "data-one-way": (SV, "_check_output", _edit("_check_output", "if got != declared:",
                                                "if any(declared.get(k) != v for k, v in got.items()):"),
                     "data_report", ()),
    "margin-substring": (SV, "margin_row_carries", _edit("margin_row_carries", "return re.search(_MARGIN_NAME + "
                                                         'r".*?" + num, line, re.IGNORECASE) is not None',
                                                         "return _num_literal(margin) in line"), "margin_exact", ()),
    "values-row-sha-only": (SV, "values_row_carries", _edit("values_row_carries", "return W42_RULE in line and "
                                                            "values_name in line and", "return True and"),
                            "margin_exact", ()),
    "provenance-pin-unchecked": (SV, "values_provenance_problems", _edit(
        "values_provenance_problems", "if not (isinstance(pin, str) and _SHA40.fullmatch(pin)):", "if False:"),
        "provenance", ()),
    "provenance-dirty-ok": (SV, "values_provenance_problems", _edit(
        "values_provenance_problems", 'elif head.endswith("-dirty"):', "elif False:"), "provenance", ()),
    "provenance-rule-skipped": (SV, "values_provenance_problems", _edit(
        "values_provenance_problems", "if why is not None:", "if False:"), "provenance", ()),
    "provenance-verify-skipped": (SV, "values_provenance_problems", _edit(
        "values_provenance_problems", "if not ok:", "if False:"), "provenance", ()),
    "invocation-argv-ignored": (SV, "invocation_problems", _edit("invocation_problems", "if bad_argv:", "if False:"),
                                "invocation", ()),
    "invocation-flags-ignored": (SV, "invocation_problems", _edit("invocation_problems", "if getattr(flags, f, 0):",
                                                                  "if False:"), "invocation", ()),
    "invocation-env-ignored": (SV, "invocation_problems", _edit("invocation_problems", "if env.get(k)]",
                                                                "if False]"), "invocation", ()),
    "driver-unbound": (SV, "objective_code", _edit("objective_code", '"driver": code_closure(DRIVER_MODULE),',
                                                   '"driver": {},'), "driver_bound", ()),
    "entry-unbound": (SV, "objective_code", _edit("objective_code", "ENTRY_SCRIPT: lf(entry_file()),",
                                                  "ENTRY_SCRIPT: None,"), "driver_bound", ()),
    "once-unchecked": (SV, "check_once_record", _edit("check_once_record", "if seen:", "if False:"), "once", ()),
    "once-unrecorded": (SV, "record_once", _edit("record_once", 'fh.write(line + "\\n")', "pass"), "once", ()),
    "once-inside-checkout": (SV, "once_location_problem", _edit(
        "once_location_problem", "if _lexically_inside(path, root) or _inside(path, root):", "if False:"), "once", ()),
    "fixture-token-real": (SV, "finalists_token", _edit("finalists_token", "if fixture:", "if False:"), "planted", ()),
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
    assert {"check_beyond", "check_se", "check_z", "check_level", "crossing_shown", "selection_value",
            "vacuous"} <= set(lim["taken_mean_p10"])                                                # n-1
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
    """M-4, each guard on its own (the entry script stood in): the invocation (m-4), a clean run, untracked files
    counted, every bound module tracked inside the repository, results only under results/, the driver the
    checkout's; then the once-record (m-5: never injected, never inside the checkout, a recorded declaration refused)
    and the values' provenance (m-3: the fixture's values are no pinned application), each before the first cell."""
    root, mine = _pinned_root(eng, tmp_path, roots, "| E-999 | 2026-11-20 | pinned `prereg/F-99_toy.md` sha256 "
                                                    "`{sha}` | t |\n")
    untracked = SV.untracked_modules
    stand_in = root / SV.ENTRY_SCRIPT                                   # a synthetic entry script, hashed at the end
    stand_in.parent.mkdir(parents=True, exist_ok=True)
    stand_in.write_bytes(b"# a stand-in entry script\n")
    try:
        monkeypatch.setattr(SV.R, "_main_script", lambda: stand_in.resolve())
        with at(root):
            with pytest.raises(SV.PartRefused, match="invoked as"):                  # m-4: pytest's own argv
                SV.run_survey(mine, results_dir=root / "results", name="x")
            monkeypatch.setattr(SV, "invocation_problems", lambda r, d: [])
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
            with pytest.raises(SV.PartRefused, match="driver's tree"):             # m-4: the checkout's own driver
                SV.run_survey(mine, results_dir=root / "results", name="x")
            monkeypatch.setattr(SV, "driver_tree", lambda: root.resolve())
            monkeypatch.setattr(SV.R, "_commit", lambda repo, what: "c" * 40)
            with pytest.raises(SV.PartRefused, match="once-record"):               # m-5: never an injected record
                SV.run_survey(mine, results_dir=root / "results", name="x", once_file=tmp_path / "o.jsonl")
            monkeypatch.setattr(SV, "ONCE_FILE", root / "survey_once.jsonl")
            with pytest.raises(SV.PartRefused, match="inside the checkout"):
                SV.run_survey(mine, results_dir=root / "results", name="x")
            once = tmp_path / "runs" / "survey_once.jsonl"
            monkeypatch.setattr(SV, "ONCE_FILE", once)
            SV.record_once(R.sha256_lf(mine), once, {"run_id": "an earlier run"})
            with pytest.raises(SV.RunRepeated, match="once-record"):
                SV.run_survey(mine, results_dir=root / "results", name="x")
            once.unlink()
            monkeypatch.setattr(SV, "_verify_result", lambda p: (True, "stood in"))  # the vendored one: own process
            with pytest.raises(SV.SpecRefused, match="not a pinned application"):   # m-3: the fixture's values
                SV.run_survey(mine, results_dir=root / "results", name="x")
            assert not once.exists()                                    # refused before the first cell: unrecorded
        with at(root):                                                 # the toy parts lie outside this tree
            assert any("outside the repository" in x for x in untracked(["survey_world"]))
    finally:
        (root / "DECISIONS.md").write_text("", encoding="utf-8")
        mine.unlink()
        stand_in.unlink()


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


# ------------------------------------------------------------------------------------------------ Q-186


def test_a_fixture_runs_token_is_refused_by_rule_1(eng, tmp_path, roots, monkeypatch):
    """m-6: what a fixture run prints is no finalists' token -- the reader's rule 1 (`_finalists`, its declaration
    check stood in) refuses it after the declaration's pin; the same run's pinned form is honoured (the control)."""
    out = survey(eng, tmp_path, roots, "plateau")
    assert out.finalists and out.token.startswith(SV.FIXTURE_TOKEN + " ")
    ref, sha = "prereg/F-99_toy.md", out.declaration_sha256
    pin = f"| E-900 | 2026-11-20 | pinned `{ref}` sha256 `{sha}` | t |\n"
    monkeypatch.setattr(R, "heldout_declaration_problems", lambda ref_, repo, market: [])
    text = pin + f"| E-901 | 2026-11-21 | {out.token} -- the finalists |\n"
    assert R.heldout_tokens(text, "finalists") == []
    with pytest.raises(R.HeldOutRefused, match="no decision row carries a finalists' token"):
        R._finalists(ref, sha, text, "a test", R.HELDOUT_PURPOSES[0], repo=tmp_path)
    real = SV.finalists_token("F-99", sha, out.list_sha256, fixture=False)
    got = R._finalists(ref, sha, pin + f"| E-901 | 2026-11-21 | {real} -- the finalists |\n", "a test",
                       R.HELDOUT_PURPOSES[0], repo=tmp_path)
    assert got.get("list") == out.list_sha256 and got.get("sha") == sha


def test_the_invocation_in_real_processes(tmp_path):
    """m-4, on a synthetic entry script in a temporary tree: run as `python scripts/survey_run.py <declaration>` it
    sees no problem; through `python -c "...runpy.run_path(...)"`, `-X utf8`, `-i`, `-m`, or with PYTHONSTARTUP set,
    it sees one."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "prereg").mkdir()
    (tmp_path / "prereg" / "F-99_x.md").write_text("synthetic\n", encoding="utf-8")
    (tmp_path / SV.ENTRY_SCRIPT).write_text(textwrap.dedent(f"""
        import json, sys
        from pathlib import Path
        sys.path.insert(0, {str(REPO)!r})
        from extended import survey as SV
        root = Path(__file__).resolve().parents[1]
        print("PROBLEMS=" + json.dumps(SV.invocation_problems(root, root / "prereg" / "F-99_x.md")), flush=True)
    """), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in SV.INVOCATION_ENV}
    env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    py, script, decl = sys.executable, SV.ENTRY_SCRIPT, "prereg/F-99_x.md"
    wrapper = (f"import runpy, sys; sys.argv = [{script!r}, {decl!r}]; "
               f"runpy.run_path({script!r}, run_name='__main__')")

    def problems(argv, extra_env=None):
        r = subprocess.run(argv, cwd=tmp_path, capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL,
                           env={**env, **(extra_env or {})})
        line = next((x for x in r.stdout.splitlines() if x.startswith("PROBLEMS=")), None)
        assert line is not None, (argv, r.returncode, r.stderr[-2000:])
        return json.loads(line[len("PROBLEMS="):])
    assert problems([py, script, decl]) == []
    for argv in ([py, "-c", wrapper], [py, "-X", "utf8", script, decl], [py, "-i", script, decl],
                 [py, "-m", "scripts.survey_run", decl]):
        assert any("invoked as" in x or "flag is set" in x for x in problems(argv)), argv
    assert problems([py, script, decl], {"PYTHONSTARTUP": str(tmp_path / "nothing.py")}) == ["PYTHONSTARTUP is set"]


def test_verify_result_in_a_process_of_its_own(tmp_path):
    """m-3: the default `_verify_result` is the vendored check (its own process): a written result verifies, an edited
    one does not, and a manifest off the vendored form fails closed (False, never an exception)."""
    code = textwrap.dedent(f"""
        import json, sys
        from pathlib import Path
        sys.path.insert(0, {str(REPO / 'tests')!r})
        import pandas as pd
        import survey_world as W
        from extended import survey as SV
        d = Path({str(tmp_path)!r})
        p, m = W._manifest_writer(pd.DataFrame({{"key": ["a"], "value_json": ["1"]}}), "v", script="x", seed=None,
                                  parameters={{}}, results_dir=d)
        a = SV._verify_result(p)[0]
        p.write_bytes(p.read_bytes() + b"b,2" + bytes([10]))
        b = SV._verify_result(p)[0]
        m.write_text(json.dumps({{"sha256": "0" * 64, "extra": 1}}), encoding="utf-8")
        c = SV._verify_result(p)[0]
        print(json.dumps([a, b, c]))
    """)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True, timeout=300, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    assert json.loads(r.stdout.strip().splitlines()[-1]) == [True, False, False]


def test_a_malformed_sidecar_refuses_as_the_spec(tmp_path, roots):
    """n-5: W42-R1's sidecar that is not JSON (or not an object) refuses as `SpecRefused`."""
    import shutil
    root = tmp_path / "root"
    shutil.copytree(roots["default"]["root"] / "results", root / "results")
    side = root / "results" / (W42.OUTPUT_NAME + ".manifest.json")
    with at(root):
        for body in ("{not json", "[1, 2]", '{"parameters": [1]}'):
            side.write_text(body, encoding="utf-8")
            with pytest.raises(SV.SpecRefused, match="sidecar"):
                SV.load_objective(W42)


def test_the_new_guards_are_in_the_suite_counts():
    """m-7: each of the red team's seven survivors, and each new guard, has its mutant here (n-4's counts)."""
    seven = {"blocks", "order", "caldigest", "paid", "untracked", "offproto", "checklevel"}
    assert seven <= set(MUTANTS) and all(MUTANTS[m][3] in SCENARIOS for m in MUTANTS)
    assert "crossing_check" not in SV.__all__ and "above_floor" in SV.W42_PUBLIC and "limit_check" in SV.W42_PUBLIC
