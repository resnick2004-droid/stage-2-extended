"""Q-126 (E-187): `scripts/q126_calibrate.py`, the calibration runner -- built ready to run, never run on the real pairs
here. Synthetic inputs only. Seeds: 20263010 (the calibration build's tests, the plan's 4.1), sub-streams by test; the
toy runs' seed maps lie outside the 2026 space (81260110 and up), named by role.

What is asserted (the plan's 6.1):
- **the seed map** is the plan's 4.1 table as parsed from the pinned file (its sha256 checked), every role in the
  block and distinct, no literal of either block outside the script's seed-block section; a map off the table refused;
- **the index orders**: the fixed streams' i, the subsets' (z_index, j), j = 0..659 with the core j < 23 identical to
  a core-only draw, the exact null index 0..33,019 against hand-built cases, the probe's seeds and model indices, the
  drift's (c, r); the null counts of the plan's 3.2 and 3.5;
- **the provenance assertion** (4.1, B-28): the full entropy of every null, the core's exact nulls included; each
  imported Q-108 construction called without a seed map refused; planted single changes refused;
- **the guard** (Q-108's, re-pointed): a literal of either block refused outside the allow-list, a derived NAME +
  constant refused, a bounded loop refused, an unbounded loop printed, another calibration plan's mention refused; on
  this repository nothing refused;
- **the choice rule on planted tables**: the primary in scope D, the scope-Q branch as the second statistic when scope D
  chooses and as the primary when it does not, NONE; condition 1 over the sizing nulls at zero tolerance; condition 3
  over the core only; condition 4 at the failure count and below it; the cost lines and whether the floor alone emptied
  a branch; ties;
- **the nesting assertion** in k and in m refusing a planted violation; the rejecting cells written only above a quarter
  of nominal;
- **the work folder**: all or none per part, a failed check kept apart and never rerun, another commit, seed map or
  package version refused, the reproduction after a code fix held file for file, the driver's order and stops;
- **the refusals** before any read (outside a clean run, the lock not this run's, a result that exists, the plan's pin
  row absent, a changed seed map), and Q-108's constructions reproduced where this runner reuses them;
- **a small end-to-end calibration on toy streams** -- every part, every candidate, both scopes, the exact enumeration
  and its re-decision with the balance limit, the probe on the sizing ranking, the drift, the power and the choice --
  that writes nothing.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
ENTRY = ROOT / "scripts" / "q126_calibrate.py"
SEED = 20263010
TOY = 81260110


def load(name="q126_calibrate_t"):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ENTRY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def pristine_q108():
    """A fresh copy of Q-108's runner, its own retired map in place (not this runner's private copy)."""
    name = "q108_calibrate_pristine_for_q126_t"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "q108_calibrate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def C():
    return load()


def toy_seeds(C):
    s = {r: TOY + i for i, r in enumerate(C.DRAW_ROLES)}
    s["tests"] = TOY + 40
    return s


def _env():
    e = {k: v for k, v in os.environ.items() if k not in ("S2X_CLEAN_RUN", "S2X_RUN_ID", "S2X_LOCK_HOLDER")}
    e.setdefault("OMP_NUM_THREADS", "1")
    return e


def _git(repo, *a):
    r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _repo(tmp_path):
    t = tmp_path / "repo"
    t.mkdir()
    _git(t, "init", "-q", "-b", "master")
    _git(t, "config", "user.email", "t@example.invalid")
    _git(t, "config", "user.name", "t")
    return t


def _write(t: Path, rel: str, text: str):
    p = t / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def synthetic_pairs(n_judged=130, per_session=10, sub=1):
    """Synthetic P-16 pairs on `n_judged` judged weekdays (Q-108's test's construction, this build's seed)."""
    rng = np.random.default_rng([SEED, sub])
    days = pd.bdate_range("2024-01-02", periods=n_judged).strftime("%Y-%m-%d").tolist()
    rows = []
    for dt in days:
        a = rng.standard_normal() * 0.5
        for j in range(per_session):
            slot = 15 * j
            r = {"date": dt, "day_kind": "n", "slot": slot, "entry_slot": slot + 1, "coin": int(rng.choice([-1, 1]))}
            for R in (1.0, 1.5, 3.0):
                kl = int(rng.random() < 1 / (1 + np.exp(-a)) * 0.9)
                ks = int(rng.random() < 1 / (1 + np.exp(a)) * 0.9)
                if not kl and rng.random() < 0.2:
                    kl = 2
                if not ks and rng.random() < 0.2:
                    ks = 2
                r[f"kl_{R:g}"], r[f"ks_{R:g}"] = kl, ks
                r[f"rl_{R:g}"] = float(R - 0.05) if kl == 1 else (float(rng.uniform(-1, R)) if kl == 2 else -1.05)
                r[f"rs_{R:g}"] = float(R - 0.05) if ks == 1 else (float(rng.uniform(-1, R)) if ks == 2 else -1.05)
                r[f"xl_{R:g}"] = slot + 1 + int(rng.integers(5, 60))
                r[f"xs_{R:g}"] = slot + 1 + int(rng.integers(5, 60))
            rows.append(r)
    p = pd.DataFrame(rows).sort_values(["date", "slot"], kind="stable").reset_index(drop=True)
    p["session"] = p["date"].map({d: i for i, d in enumerate(days)}).astype(np.int64)
    return p, days


# ------------------------------------------------------------------------------------------------ the seed map


def test_the_seed_map_is_the_plans_table(C):
    text = C.plan_path().read_text(encoding="utf-8")
    want, spare = C.parsed_seed_map(text, "calibration", C.ROLE_TEXT)
    assert C.SEEDS == want and spare == [] and C.SPARE == ()
    assert set(C.SEEDS.values()) == set(C.CAL_BLOCK) and C.SEEDS["tests"] == SEED
    assert C.seed_map_problems(C.SEEDS, C.CAL_BLOCK, C.DRAW_ROLES + ("tests",)) == []
    assert C.file_sha_lf(C.plan_path()) == C.PLAN_SHA256
    vmap, vspare = C.parsed_seed_map(text, "validation", load_validate().ROLE_TEXT)
    assert len(vmap) == 9 and len(vspare) == 1 and set(vmap.values()) | set(vspare) == set(C.VAL_BLOCK)


def test_a_seed_map_off_the_table_is_refused(C, monkeypatch):
    roles = C.DRAW_ROLES + ("tests",)
    swap = dict(C.SEEDS, drift=C.SEEDS["probe"], probe=C.SEEDS["drift"])        # in the block, distinct, misplaced
    assert any("not the plan's 4.1" in p for p in C.seed_map_problems(swap, C.CAL_BLOCK, roles))
    q108 = dict(C.SEEDS, fixed_mc=pristine_q108().SEEDS["fixed_mc"])            # Q-108's retired seed
    assert any("outside this runner's block" in p for p in C.seed_map_problems(q108, C.CAL_BLOCK, roles))
    assert any("spare" in p for p in C.seed_map_problems(C.SEEDS, C.CAL_BLOCK, roles, spare=(C.VAL_BLOCK[-1],)))
    monkeypatch.setattr(C, "PLAN_SHA256", "0" * 64)
    assert any("pin" in p for p in C.seed_map_problems(C.SEEDS, C.CAL_BLOCK, roles))


def test_every_manifests_seed_map_is_checked_against_the_pinned_table(C):
    V = load_validate()
    assert C.manifest_seed_problems(C.SEEDS) == [] and C.manifest_seed_problems(V.SEEDS) == []
    assert C.manifest_seed_problems(dict(C.SEEDS, drift=C.SEEDS["probe"], probe=C.SEEDS["drift"]))
    assert C.manifest_seed_problems(dict(V.SEEDS, drift=V.SPARE[0]))               # the spare is drawn by nothing
    assert C.manifest_seed_problems({"tests": TOY})
    with pytest.raises(C.ProvenanceRefused):
        C._manifest_base(dict(C.SEEDS, subsets=C.SEEDS["subset_mc"], subset_mc=C.SEEDS["subsets"]))
    assert C._manifest_base(C.SEEDS)["seed_map"] == C.SEEDS


def test_seed_literals_only_in_the_seed_block_section(C):
    src = ENTRY.read_text(encoding="utf-8")
    lines = src.splitlines()
    first = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- the seed blocks"))
    last = next(i for i, x in enumerate(lines, 1) if x.startswith("# ---- end of the seed blocks"))
    lits = [(node.lineno, node.value) for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Constant)
            and isinstance(node.value, int) and 20263000 <= node.value <= 20263099]
    assert lits and all(first < ln < last for ln, _ in lits), lits
    assert {v for _, v in lits} == set(C.CAL_BLOCK) | {C.CAL_BLOCK[-1] + 1, C.VAL_BLOCK[-1] + 1}
    # no Q-108 seed is written in this runner (its blocks are named only through its own retired map)
    assert not any(20262000 <= v <= 20262199 for _, v in lits)


# ------------------------------------------------------------------------------------------------ the indices


def test_the_index_orders(C):
    s = C.SEEDS
    core = {x["null"]: x for x in C.core_plan(s)}
    fx = [x for x in core.values() if x["group"] == "fixed" and x["kind"] == "mc"]
    assert sorted(x["entropy"][1] for x in fx) == list(range(28))
    assert core["fixed:taken:net3:markov80"]["entropy"] == [s["fixed_mc"], 27]
    assert core["sub:2000:003:net3:coin"]["entropy"] == [s["subset_mc"], 3, 3, 1, 6]
    assert "sub:2000:017:net3:coin" not in core and "sub:2000:017:net3:markov50" in core
    # the exact null index (4.1), hand-built: data (offered, taken, the subsets by z_index then j), value, model
    hand = {"fixed:offered:win1:flip42": 0, "fixed:offered:win1:alt55": 4, "fixed:offered:net3:flip42": 5,
            "fixed:taken:net3:alt55": 19, "sub:200:000:win1:flip42": 20, "sub:200:000:win1:flip55": 21,
            "sub:200:000:net3:flip42": 25, "sub:200:001:win1:flip42": 30, "sub:200:022:net3:alt55": 249,
            "sub:500:000:win1:flip42": (2 + 660) * 10, "sub:5000:022:net3:alt55": ((2 + 4 * 660 + 22) * 2 + 1) * 5 + 4}
    for k, v in hand.items():
        assert core[k]["exact_index"] == v and core[k]["sample_entropy"] == [s["exact_sample"], v], k
    sizing = {x["null"]: x for z in C.SIZES for x in C.sizing_plan(s, z)}
    assert sizing["sub:200:023:win1:flip42"]["exact_index"] == (2 + 23) * 10
    assert sizing["sub:5000:659:net3:alt55"]["exact_index"] == 33019
    assert all(x["sample_entropy"] is None for x in sizing.values())            # no uniform cells on the sizing nulls
    allx = [x["exact_index"] for x in [*core.values(), *sizing.values()] if x["kind"] == "exact"]
    assert sorted(allx) == list(range(33020))
    # the sizing subsets continue the core's j: j = 23..659, each subset by [s, z_index, j]
    js = sorted({x["j"] for x in sizing.values() if x["size"] == 1000})
    assert js == list(range(23, 660))
    assert sizing["sub:1000:600:net3:flip63"]["subset_entropy"] == [s["subsets"], 2, 600]
    # the core j < 23 is a core-only draw: one subset's draw depends on (z, j) and the seed alone
    a = C.CAL.subset_index(5000, 1000, [s["subsets"], 2, 7])
    b = C.CAL.subset_index(5000, 1000, core["sub:1000:007:win1:alt45"]["subset_entropy"])
    assert np.array_equal(a, b)
    # the probe: its role's seed, the subset's own j, Q-108's model_index (2, 9, 10, 11)
    pp = C.probe_plan(s, {200: [(400, Fraction(3))], 5000: [(23, Fraction(1))]})
    assert [x["model_index"] for x in pp[:4]] == [2, 9, 10, 11]
    assert pp[0]["entropy"] == [s["probe"], 0, 400, 0, 2] and pp[0]["subset_entropy"] == [s["subsets"], 0, 400]
    assert pp[-1]["entropy"] == [s["probe"], 4, 23, 1, 11]
    dr = C.drift_plan(s)
    assert dr[0]["entropy"] == [s["drift"], 0, 0] and dr[-1]["entropy"] == [s["drift"], 7, 149]
    assert [x["model"] for x in dr[:5]] == list(C.EXACT_MODELS)


def test_the_null_counts(C):
    got = C.expected_counts(C.SEEDS)
    assert got == C.EXPECTED == {"core_rule": 2293, "core_exact": 1170, "core_mc": 1123, "beside_cp": 54,
                                 "beside_flat": 30, "sizing": 31850, "probe": 920, "drift": 6000, "rule": 35063,
                                 "exact_index_max": 33019}
    assert C.PARTS == ("core", "sizing200", "sizing500", "sizing1000", "sizing2000", "sizing5000", "probe", "drift",
                       "choice")
    toys = [x for x in C.core_plan(C.SEEDS) if x["toy"]]
    assert sum(x["toy"] == "P" for x in toys) == 10 and [x["null"] for x in toys if x["toy"] == "cluster"] == \
        ["syn:cluster:1000"]


# ------------------------------------------------------------------------------------------------ provenance


def test_the_provenance_assertion_holds_the_full_entropy(C):
    s = C.SEEDS
    plan = C.deterministic_plan(s)
    assert C.provenance_problems(plan, s, C.CAL_BLOCK) == []
    pr = C.probe_plan(s, {z: [(23 + i, Fraction(1)) for i in range(23)] for z in C.SIZES})
    assert len(pr) == 920 and C.provenance_problems(pr, s, C.CAL_BLOCK) == []
    import copy

    def refused(mut):
        p2 = copy.deepcopy(plan[:3000] + pr[:10] + plan[-10:])
        mut(p2)
        return C.provenance_problems(p2, s, C.CAL_BLOCK)

    def at(p2, name):
        return next(x for x in p2 if x["null"] == name)

    assert refused(lambda p2: at(p2, "fixed:offered:net3:flip5").update(entropy=[s["fixed_mc"], 1]))
    # a core exact null carrying Q-108's index (2 + z_index x 23 + j) -- the red team's n4
    q108_xi = ((2 + 1 * 23 + 0) * 2 + 0) * 5
    assert refused(lambda p2: at(p2, "sub:500:000:win1:flip42").update(
        exact_index=q108_xi, sample_entropy=[s["exact_sample"], q108_xi]))
    assert refused(lambda p2: at(p2, "sub:500:000:win1:markov30").update(
        entropy=[s["subset_mc"], 1, 0, 0, 10]))                                  # another model's index
    assert refused(lambda p2: p2[3000].update(entropy=[s["subset_mc"], *p2[3000]["entropy"][1:]]))  # probe -> core role
    assert refused(lambda p2: p2[-1].update(entropy=[s["drift"], 7, 148]))
    assert refused(lambda p2: at(p2, "sub:200:000:net3:flip63").update(subset_entropy=[s["subsets"], 0, 1]))
    assert refused(lambda p2: at(p2, "syn:iid:200").update(entropy=[TOY, 0]))   # off the block


def test_each_imported_q108_construction_without_a_seed_map_is_refused(C, monkeypatch):
    """The plan's 4.1 build test: Q-108's `null_plan` and `expected_counts` fall back to Q-108's retired map. In this
    runner's private copy they refuse; their output in Q-108's own copy is refused by the provenance assertion."""
    with pytest.raises(C.ProvenanceRefused):
        C.CAL.null_plan()
    with pytest.raises(C.ProvenanceRefused):
        C.CAL.expected_counts()
    with pytest.raises(C.ProvenanceRefused):
        C.CAL.compute_part("syn", None, 130, 10, C.SEEDS, ["cons"], None)       # never this run's, map or none
    with pytest.raises(C.ProvenanceRefused):
        C.CAL.main([])
    with pytest.raises(TypeError):
        C.CAL.Inputs(None, 130, None)                                           # the inputs take a map, always
    Q = pristine_q108()
    old = Q.null_plan()                                                         # Q-108's own retired map
    probs = C.provenance_problems([dict(C._base(), **x) for x in old], C.SEEDS, C.CAL_BLOCK)
    assert probs and sum("is not the plan's" in p for p in probs) >= len(old) * 0.9
    seen = {}
    real = Q.null_plan

    def spy(seeds=None):
        seen["plan"] = real(seeds)
        return seen["plan"]
    monkeypatch.setattr(Q, "null_plan", spy)
    Q.expected_counts()
    assert C.provenance_problems([dict(C._base(), **x) for x in seen["plan"]], C.SEEDS, C.CAL_BLOCK)
    # with this plan's map but Q-108's construction: its exact index (n4) and its subsets' j are refused all the same
    mine = Q.null_plan(C.SEEDS)
    probs = C.provenance_problems([dict(C._base(), **x) for x in mine], C.SEEDS, C.CAL_BLOCK)
    assert any("exact index" in p for p in probs)


# ------------------------------------------------------------------------------------------------ the guard


def test_the_guard_on_literals_and_derived_seeds(C, tmp_path):
    t = _repo(tmp_path)
    _write(t, "scripts/q126_calibrate.py", "SEEDS = {'a': 20263011}\n")             # allowed
    _write(t, "docs/notes.md", "the blocks 20263010-20263029 are reserved\n")       # a document's mention
    _write(t, "other.py", "SEED = 202630111\n")                                     # not word-bounded
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "c")
    probs, notes = C.seed_block_problems(t)
    assert probs == [] and any("notes.md" in n for n in notes)
    _write(t, "docs/calibration/Q-999_other_plan.md", "seed 20263025\n")          # another calibration plan
    probs, _ = C.seed_block_problems(t)
    assert any("Q-999_other_plan.md" in p for p in probs)
    (t / "docs" / "calibration" / "Q-999_other_plan.md").unlink()
    code = "\n".join(["BASE = 20263000", "lands = BASE + 15", "misses = BASE + 30",
                      "for i in range(4):", "    f(BASE + 27 + i)",
                      "for i, x in enumerate(stuff):", "    f(BASE + 2 + i)"]) + "\n"
    _write(t, "x.py", code)
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "derived")
    probs, notes = C.seed_block_problems(t)
    got = sorted(p.split("`")[1] for p in probs if "`" in p)
    assert got == ["BASE + 15", "BASE + 27 + i"], probs
    assert any("BASE + 2 + i" in n and "NOT in the hand-check record" in n for n in notes)
    _git(t, "checkout", "-q", "-b", "side")
    _write(t, "extended/stray.py", "rng = default_rng([20263013, 1])\n")
    _git(t, "add", "-A")
    _git(t, "commit", "-q", "-m", "a stray use")
    _git(t, "checkout", "-q", "master")
    probs, _ = C.seed_block_problems(t)
    assert any("extended/stray.py" in p and "side" in p for p in probs)


def test_the_guard_on_this_repository(C):
    probs, notes = C.seed_block_problems(ROOT)
    assert probs == [], probs
    printed = [n for n in notes if n.startswith("derived seed") and "`" in n]
    assert all("hand-checked" in n for n in printed), printed


# ------------------------------------------------------------------------------------------------ the choice rule


def _row(C, null, kind, group, c, s_, den, model, size=None, j=None, counts=None, in_rule=True):
    r = {"null": null, "kind": kind, "group": group, "in_rule": in_rule, "candidate": c, "scope": s_,
         "denominator": den, "model": model, "size": size, "j": j}
    counts = counts or [0] * 8
    for lab, x in zip(C.LABELS, list(counts) + [0] * 4):
        r[f"count_{lab}"] = x
    return r


FDEN = 42 * 2 ** 17


def planted(C, sizes=(200, 5000), core_j=(0,), sizing_j=(23, 24)):
    rows = []
    for c in C.CANDS:
        for s_ in C.SCOPES:
            rows += [_row(C, f"mc{i}", "mc", "subset", c, s_, 200_000, "markov50", 200, 0) for i in range(3)]
            rows.append(_row(C, "syn:iid:200", "mc", "synthetic", c, s_, 200_000, "iid"))
            rows.append(_row(C, "fixed:offered:win1:flip42", "exact", "fixed", c, s_, FDEN, "flip42"))
            for z in sizes:
                for j in (*core_j, *sizing_j):
                    for m in ("flip42", "alt45"):
                        g = "subset" if j < C.N_CORE else "sizing"
                        rows.append(_row(C, f"sub:{z}:{j:03d}:win1:{m}", "exact", g, c, s_, FDEN if m == "flip42"
                                         else 90, m, z, j))
                rows.append(_row(C, f"probe:{z}:023:win1:markov50", "mc", "probe", c, s_, 200_000, "markov50", z, 23))
    return pd.DataFrame(rows)


def _set(C, df, c, s_, null, counts):
    sel = (df["candidate"] == c) & (df["scope"] == s_) & (df["null"] == null)
    assert sel.sum() == 1, null
    for lab, x in zip(C.FAM_LABELS, counts):
        df.loc[sel, f"count_{lab}"] = x


P_BASE = {"cons": 1.0, "cons_m1.125": 1.1, "cons_m1.25": 1.2, "cons_m1.375": 1.3, "cons_m1.5": 1.4,
          "cons_m1.75": 1.6, "cons_m2": 1.8, "cons_bm_m1.25": 1.21}


def _power(C, P):
    rows = []
    for c in C.CANDS:
        for s_ in C.SCOPES:
            for t in range(10):
                for k in C.POWER_KS:
                    rows.append({"row": "toy", "null": f"toy{t}", "toy": "P", "candidate": c, "scope": s_, "k": k,
                                 "mdl50": P[c] / 2, "mdl80": P[c] * (1.1 if t % 2 else 1 / 1.1)})
    return pd.DataFrame(rows)


def _choose(C, size, P=P_BASE):
    return C.choose(C.eligibility(size), C.power_summary(_power(C, P)))


def _t(ch):
    return ch["table"].set_index(["candidate", "scope"])


def test_the_primary_in_scope_d_and_the_second_statistic(C):
    ch = _choose(C, planted(C))
    assert ch["line"] == "CHOSEN cons (scope D)\nSECOND cons_m1.5 (scope Q)"
    t = _t(ch)
    assert not t.loc[("cons", "Q"), "eligible"] and not t.loc[("cons", "Q"), "in_rule"]       # beside, never chosen
    assert t.loc[("cons_m1.5", "Q"), "in_rule"] and not t.loc[("cons_bm_m1.25", "Q"), "in_rule"]
    assert t.loc[("cons", "D"), "chosen"] == "primary" and t.loc[("cons_m1.5", "Q"), "chosen"] == "second"
    fr = C.choice_frame(ch)
    assert fr[fr["row"] == "decision"]["decision"].iloc[0] == "CHOSEN cons (scope D); SECOND cons_m1.5 (scope Q)"
    ps = C.power_summary(_power(C, P_BASE))
    assert float(ps[(ps["candidate"] == "cons_m2") & (ps["scope"] == "D")]["P_rel_cons_m1.25"].iloc[0]) == \
        pytest.approx(1.8 / 1.2)
    # ties: at the same P and members, the earlier row
    ch = _choose(C, planted(C), dict(P_BASE, cons=1.21, **{"cons_m1.125": 1.21, "cons_m1.25": 1.21,
                                                           "cons_bm_m1.25": 1.21}))
    assert ch["line"].startswith("CHOSEN cons (scope D)")
    ch = _choose(C, planted(C), dict(P_BASE, cons=1.5, **{"cons_m1.125": 1.5, "cons_m1.25": 1.21,
                                                          "cons_bm_m1.25": 1.21}))
    assert ch["line"].startswith("CHOSEN cons_m1.25 (scope D)")                       # row 3 before row 8
    ch = _choose(C, planted(C), dict(P_BASE, **{"cons_m1.75": 1.4}))                 # m1.5 before m1.75 at one P
    assert ch["line"].endswith("SECOND cons_m1.5 (scope Q)")


def test_condition_1_over_the_sizing_nulls_at_zero_tolerance(C):
    size = planted(C)
    # one bad sizing subset (an alternating configuration rejecting at every k) for cons and cons_m1.125 in scope D
    for c in ("cons", "cons_m1.125"):
        _set(C, size, c, "D", "sub:5000:024:win1:alt45", [1] * 8)
    ch = _choose(C, size)
    t = _t(ch)
    assert t.loc[("cons", "D"), "bad_subsets"] == 1 and t.loc[("cons", "D"), "bad_sizing_subsets"] == 1
    assert t.loc[("cons", "D"), "bad_subsets_5000"] == 1 and t.loc[("cons", "D"), "bad_subsets_alt45"] == 1
    assert not t.loc[("cons", "D"), "cond1_floors"] and t.loc[("cons", "D"), "refused_by_cond1_sized_alone"]
    assert ch["line"].startswith("CHOSEN cons_m1.25 (scope D)")
    cost = [r for r in ch["cost"] if r["row"] == "cost" and "sized" in r["decision"] and r["scope"] == "D"]
    assert cost and cost[0]["candidate"] == "cons" and cost[0]["refusing_count"] == 1
    # a flip-42 sizing null just above nominal at k = 20 only: 1 bad subset (one in the 3,300 refuses)
    size = planted(C)
    x = FDEN // (20 * 20 * 21) + 1
    _set(C, size, "cons_m1.25", "D", "sub:200:023:win1:flip42", [x] * 8)
    t = _t(_choose(C, size))
    assert t.loc[("cons_m1.25", "D"), "bad_subsets"] == 1 and not t.loc[("cons_m1.25", "D"), "eligible"]
    size = planted(C)
    _set(C, size, "cons_m1.25", "D", "sub:200:023:win1:flip42", [x - 1] * 8)            # at nominal: not bad
    t = _t(_choose(C, size))
    assert t.loc[("cons_m1.25", "D"), "bad_subsets"] == 0
    # the ratio there (0.99 of nominal at k = 20) is a sizing null's: condition 3 does not see it
    assert t.loc[("cons_m1.25", "D"), "cond3_ratio"] and t.loc[("cons_m1.25", "D"), "eligible"]
    assert t.loc[("cons_m1.25", "D"), "worst_exact_ratio_all"] > 0.99 > t.loc[("cons_m1.25", "D"),
                                                                                "worst_exact_ratio_core"]


def test_condition_3_over_the_core_only(C):
    size = planted(C)
    x = FDEN // (20 * 20 * 21) // 2                                                     # 0.5 of nominal at k = 20
    _set(C, size, "cons", "D", "sub:200:000:win1:flip42", [x] * 8)                      # a core subset: refused
    _set(C, size, "cons_m1.125", "D", "sub:200:024:win1:flip42", [x] * 8)               # a sizing subset: not
    t = _t(_choose(C, size))
    assert not t.loc[("cons", "D"), "cond3_ratio"] and t.loc[("cons", "D"), "refused_by_cond3_alone"]
    assert t.loc[("cons", "D"), "worst_exact_k_core"] == 20
    assert t.loc[("cons_m1.125", "D"), "cond3_ratio"] and t.loc[("cons_m1.125", "D"), "eligible"]
    q = FDEN // (20 * 20 * 21) // 4                                                     # at most a quarter: passes
    size = planted(C)
    _set(C, size, "cons", "D", "fixed:offered:win1:flip42", [q] * 8)
    assert _t(_choose(C, size)).loc[("cons", "D"), "cond3_ratio"]
    _set(C, size, "cons", "D", "fixed:offered:win1:flip42", [q + 1] * 8)
    assert not _t(_choose(C, size)).loc[("cons", "D"), "cond3_ratio"]


def test_condition_4_the_probe_at_its_failure_count(C):
    fail = [C.CAL.FAIL[k] for k in C.KS]
    assert fail == [71, 63, 56, 50, 45, 41, 38, 35]
    size = planted(C)
    below = [f - 1 for f in fail]
    below = [min(below[i:]) for i in range(8)]                          # non-increasing in k
    _set(C, size, "cons", "D", "probe:5000:023:win1:markov50", below)
    t = _t(_choose(C, size))
    assert t.loc[("cons", "D"), "cond4_probe"] and t.loc[("cons", "D"), "probe_worst_share"] == pytest.approx(34 / 35)
    _set(C, size, "cons", "D", "probe:5000:023:win1:markov50", [35] * 8)              # 35 at k = 20: its count
    ch = _choose(C, size)
    t = _t(ch)
    assert not t.loc[("cons", "D"), "cond4_probe"] and t.loc[("cons", "D"), "refused_by_cond4_alone"]
    assert t.loc[("cons", "D"), "probe_worst_k"] == 20 and t.loc[("cons", "D"), "probe_worst_count"] == 35
    # the probe is not in P_MC or the point-rate floor (B-29): 35 of 200,000 is below nominal at k = 13 anyway
    assert t.loc[("cons", "D"), "p_mc"] == 1.0 and t.loc[("cons", "D"), "mc_floor_ok"]
    assert ch["line"].startswith("CHOSEN cons_m1.125 (scope D)")


def test_the_scope_q_branch_as_the_primary_none_and_the_floor_emptying_a_branch(C):
    size = planted(C)
    for c in C.CANDS:
        _set(C, size, c, "D", "sub:200:023:win1:alt45", [1] * 8)                         # every scope-D row: bad
    ch = _choose(C, size)
    assert ch["line"] == "CHOSEN cons_m1.5 (scope Q)" and ch["second"] is None and ch["primary"]["scope"] == "Q"
    em = {r["scope"]: r for r in ch["cost"] if r["row"] == "floor_emptied_branch"}
    assert em["D"]["branch_empty"] and em["D"]["floor_alone_emptied"] and not em["Q"]["branch_empty"]
    for c in C.L2.Q_BRANCH:
        _set(C, size, c, "Q", "mc0", [100] * 8)                                          # point rate above nominal
    ch = _choose(C, size)
    assert ch["line"] == "NONE" and ch["primary"] is None
    em = {r["scope"]: r for r in ch["cost"] if r["row"] == "floor_emptied_branch"}
    assert em["Q"]["branch_empty"] and not em["Q"]["floor_alone_emptied"]          # the MC floor, not the sized one
    assert C.choice_frame(ch)[lambda d: d["row"] == "decision"]["decision"].iloc[0] == "NONE"
    # P_MC below 0.9 refuses (condition 2): five nulls each just below nominal at every k
    size = planted(C)
    for i in range(3):
        _set(C, size, "cons", "D", f"mc{i}", [54, 47, 41, 36, 32, 29, 26, 23])
    t = _t(_choose(C, size))
    want = C.CAL.p_holds([x / 200_000 for x in (54, 47, 41, 36, 32, 29, 26, 23)]) ** 3
    assert t.loc[("cons", "D"), "p_mc"] == pytest.approx(want) and (want < 0.9) == (not t.loc[("cons", "D"),
                                                                                              "cond2_p_mc"])


# ------------------------------------------------------------------------------------------------ the failed checks


def test_the_nesting_assertion_in_k_and_in_m(C):
    e = {"null": "x"}
    z = np.zeros(12, dtype=np.int64)
    counts = {(c, s): z.copy() for c in C.CANDS for s in C.SCOPES}
    assert C.nesting_problems(e, {"counts": counts}, list(C.CANDS)) == []
    counts[("cons", "Q")] = np.array([3, 3, 4, 2, 2, 1, 0, 0, 9, 9, 9, 9])
    probs = C.nesting_problems(e, {"counts": counts}, list(C.CANDS))
    assert any("rise with k" in p for p in probs)
    counts[("cons", "Q")] = z.copy()
    counts[("cons_m1.375", "D")] = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1])     # above cons_m1.25's zeros
    probs = C.nesting_problems(e, {"counts": counts}, list(C.CANDS))
    assert len(probs) == 1 and "not nested in m" in probs[0] and "scope D" in probs[0]
    counts[("cons_m1.375", "D")] = z.copy()
    counts[("cons_bm_m1.25", "D")] = np.array([5] * 12)                                # row 8: not nested, no check
    assert C.nesting_problems(e, {"counts": counts}, list(C.CANDS)) == []
    size = planted(C)
    _set(C, size, "cons_m2", "Q", "mc1", [2] * 8)                                        # above cons_m1.75's zeros
    assert C.nesting_in_m_table(size)


def test_the_rejecting_cells_are_written_only_above_a_quarter(C):
    rec = {"cell": np.array([3, 9]), "p": np.array([0, 1]), "q": np.array([3, 1]), "B": np.array([16, 16]),
           "weight": np.array([2, 2]), "admitted": np.array([1, 1]), "kmax": np.array([20, 14])}
    den = FDEN
    quarter = den // (4 * 20 * 13 * 14)                                                 # a quarter of nominal at k = 13
    e = {"null": "sub:200:000:win1:flip42", "part": "core", "group": "subset", "model": "flip42"}
    res = {"den": den, "records": {("cons", "D"): rec}, "counts": {("cons", "D"): [quarter] + [0] * 11}}
    assert C.cell_rows(e, res) == []                                                    # at a quarter: not written
    res["counts"][("cons", "D")] = [quarter + 1] + [0] * 11
    rows = C.cell_rows(e, res)
    assert [r["cell"] for r in rows] == [3, 9] and rows[0]["k_max"] == 20 and rows[1]["blocks"] == 16
    assert all(r["candidate"] == "cons" and r["scope"] == "D" and r["first"] is None for r in rows)
    e2 = dict(e, model="alt45")
    res2 = {"den": 90, "records": {("cons", "D"): dict(rec, q=np.array([1, 0]), B=np.array([-1, -1]))}, "counts": {("cons", "D"): [1] + [0] * 11}}
    rows = C.cell_rows(e2, res2)
    assert [r["first"] for r in rows] == ["short", "long"] and rows[0]["blocks"] is None


# ------------------------------------------------------------------------------------------------ the work folder


def _out(C, part, failed_=False):
    o = C._empty_out(part)
    o["size"] = [{"null": "a", "x": 1}]
    o["meta"] = {"part": part}
    if failed_:
        o["nesting"] = ["planted"]
    return o


def test_a_part_is_written_all_or_none(C, tmp_path, monkeypatch):
    work = tmp_path / "work"
    man = {"commit": "c1", "seed_map": {"a": 1}, "versions": {"numpy": "1"}}
    d = C.write_part(work, "sizing200", _out(C, "sizing200"), man)
    assert d == work / "sizing200" and (d / "manifest.json").is_file()
    m = C.read_manifest(d)
    assert set(m["files"]) == {"size.csv", "power.csv", "cells.csv", "mismatches.csv", "ranking.csv"}
    assert C.part_problems(work, "sizing200", commit="c1", seeds={"a": 1}) == []
    assert C.part_problems(work, "sizing200", commit="c2", seeds={"a": 1})
    assert C.part_problems(work, "sizing200", commit="c1", seeds={"a": 2})
    assert C.part_problems(work, "sizing200", commit="c1", seeds={"a": 1}, versions={"numpy": "2"})
    (d / "size.csv").write_text("null,x\nb,2\n", encoding="utf-8")                      # tampered
    assert any("does not hash" in p for p in C.part_problems(work, "sizing200", commit="c1", seeds={"a": 1}))
    # a crash in the middle of the writing leaves no part and no partial folder
    real = pd.DataFrame.to_csv
    calls = {"n": 0}

    def boom(self, *a, **k):
        calls["n"] += 1
        if calls["n"] == 3:
            raise OSError("planted crash")
        return real(self, *a, **k)
    monkeypatch.setattr(pd.DataFrame, "to_csv", boom)
    with pytest.raises(OSError):
        C.write_part(work, "sizing500", _out(C, "sizing500"), man)
    monkeypatch.setattr(pd.DataFrame, "to_csv", real)
    assert not (work / "sizing500").exists() and not list(work.glob(".sizing500.tmp-*"))
    # a failed check is kept apart, never as output
    d = C.write_part(work, "sizing1000", _out(C, "sizing1000", failed_=True), man)
    assert d.name == "sizing1000.failed" and not (work / "sizing1000").exists()
    assert C.part_problems(work, "sizing1000", commit="c1", seeds={"a": 1})
    # the package versions: one part of another environment is refused by the choice
    C.write_part(work, "sizing2000", _out(C, "sizing2000"), dict(man, versions={"numpy": "2"}))
    C.write_part(work, "sizing5000", _out(C, "sizing5000"), man)
    assert C.versions_problems(work, ["sizing5000"]) == []
    assert C.versions_problems(work, ["sizing5000", "sizing2000"])


def test_the_driver_order_stops_and_reproduction(C, tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.setattr(C, "git_head", lambda repo=None: "commitB")
    ran = []

    def step_ok(name, args, log_file=None):
        part = args[2]
        ran.append(part)
        if part != "choice":
            C.write_part(work, part, _out(C, part), {"commit": "commitB", "seed_map": {}, "versions": {}})
        return 0
    assert C.driver(C.PARTS, work, step=step_ok) == 0
    assert ran == list(C.PARTS)
    ran.clear()
    assert C.driver(C.PARTS, work, step=step_ok) == 0 and ran == ["choice"]            # whole parts are not rerun
    # a code fix: commit C; every whole part of commit B is moved aside and must be reproduced file for file
    monkeypatch.setattr(C, "git_head", lambda repo=None: "commitC")
    ran.clear()

    def step_c(name, args, log_file=None):
        part = args[2]
        ran.append(part)
        if part != "choice":
            o = _out(C, part)
            if part == "probe":
                o["size"] = [{"null": "a", "x": 2}]                                      # differs
            C.write_part(work, part, o, {"commit": "commitC", "seed_map": {}, "versions": {}})
        return 0
    assert C.driver(C.PARTS, work, step=step_c) == C.FAILED_CHECK
    assert ran[-1] == "probe" and (work / "probe.prev-commitB").is_dir()
    assert C.reproduction_problems(work, "sizing200") == []
    assert C.reproduction_problems(work, "probe")
    # a crash: the driver stops, nothing after it runs; a partial folder is no output
    w2 = tmp_path / "w2"
    w2.mkdir()
    (w2 / ".core.tmp-123").mkdir()
    ran.clear()

    def step_crash(name, args, log_file=None):
        ran.append(args[2])
        return 1
    assert C.driver(C.PARTS, w2, step=step_crash) == 1 and ran == ["core"]
    assert not (w2 / ".core.tmp-123").exists()

    def step_fail(name, args, log_file=None):
        ran.append(args[2])
        return C.FAILED_CHECK
    ran.clear()
    assert C.driver(C.PARTS, w2, step=step_fail) == C.FAILED_CHECK and ran == ["core"]


# ------------------------------------------------------------------------------------------------ the refusals


def test_refuses_outside_a_clean_run_before_any_step():
    r = subprocess.run([sys.executable, str(ENTRY)], cwd=str(ROOT), capture_output=True, text=True, timeout=600,
                       env=_env())
    assert r.returncode == 3 and "REFUSED" in r.stdout and "clean run" in r.stdout, r.stdout[-2000:] + r.stderr
    assert "step" not in r.stdout.lower()
    r = subprocess.run([sys.executable, str(ENTRY), "--part", "core"], cwd=str(ROOT), capture_output=True, text=True,
                       timeout=600, env=_env())
    assert r.returncode == 3 and "clean run" in r.stdout


def test_the_lock_must_be_this_runs(C, tmp_path, monkeypatch):
    from extended import lock_guard

    monkeypatch.setattr(lock_guard, "main_root", lambda start=None: tmp_path)
    assert "not held by this run" in C.lock_problem({"S2X_CLEAN_RUN": "q126-calibrate"})
    env = {"S2X_CLEAN_RUN": "q126-calibrate", "S2X_LOCK_HOLDER": "q126-calibrate"}
    assert "names job None" in C.lock_problem(env)
    (tmp_path / "run.lock").write_text(json.dumps({"job": "other-job"}), encoding="utf-8")
    assert "other-job" in C.lock_problem(env)
    (tmp_path / "run.lock").write_text(json.dumps({"job": "q126-calibrate"}), encoding="utf-8")
    assert C.lock_problem(env) is None
    assert C.lock_problem(dict(env, S2X_LOCK_HOLDER="another")) is not None


def test_the_preflight_refusals(C, monkeypatch, tmp_path, capsys):
    from extended import results as XR

    monkeypatch.setattr(XR, "clean_run_problem", lambda: None)
    monkeypatch.setattr(C, "lock_problem", lambda env=None: "the run lock is not held by this run")
    assert C.preflight(tmp_path, None, guard=False) == ["the run lock is not held by this run"]
    monkeypatch.setattr(C, "lock_problem", lambda env=None: None)
    (tmp_path / "q126_choice.csv").write_text("x\n", encoding="utf-8")
    assert any("never overwritten" in p for p in C.preflight(tmp_path, None, guard=False))
    assert not any("never overwritten" in p for p in C.preflight(tmp_path, "core", guard=False))
    (tmp_path / "q126_choice.csv").unlink()
    # the plan's pin row: a DECISIONS.md without E-187's row naming the pinned path and sha256 refuses
    repo = tmp_path / "repo"
    for rel in [*C.VALIDATED_BLOBS, C.PLAN_NAMES[1] if (ROOT / C.PLAN_NAMES[1]).is_file() else C.PLAN_NAMES[0]]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_bytes((ROOT / rel).read_bytes())
    (repo / "DECISIONS.md").write_text("| E-001 | x |\n", encoding="utf-8")
    assert any("not pinned" in p for p in C.pin_problems(repo))
    row = f"| E-187 | 2026-11-17 | **pinned: `{C.PLAN_NAMES[0]}` sha256 `{C.PLAN_SHA256}`** | basis |\n"
    (repo / "DECISIONS.md").write_text(row, encoding="utf-8")
    assert C.pin_problems(repo) == []
    (repo / "extended" / "lift_bound.py").write_text("# changed\n", encoding="utf-8")
    assert any("lift_bound" in p for p in C.pin_problems(repo))
    # with the pin mocked as present: the seed map and the provenance assertion
    monkeypatch.setattr(C, "pin_problems", lambda repo=None: [])
    monkeypatch.setattr(C, "work_dir", lambda: tmp_path / "outside")
    assert C.preflight(tmp_path, None, guard=False) == []
    bad = dict(C.SEEDS, probe=C.SEEDS["drift"], drift=C.SEEDS["probe"])
    assert any("not the plan's 4.1" in p for p in C.preflight(tmp_path, None, seeds=bad, guard=False))
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "sizing500.failed").mkdir()
    assert any("failed check is on record" in p for p in C.preflight(tmp_path, None, guard=False))
    # main() stops at the first refusal, before any step
    monkeypatch.setattr(C, "lock_problem", lambda env=None: "the run lock is not held by this run")
    assert C.main([]) == 3
    out = capsys.readouterr().out
    assert "REFUSED" in out and "step" not in out


def test_the_runs_pin_row_is_not_yet_in_this_tree_or_is_e187s(C):
    """Until E-187's row is in DECISIONS.md the run refuses; once it is, the pin passes (whichever the tree holds)."""
    dec = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    probs = C.pin_problems(ROOT)
    if f"`{C.PLAN_NAMES[0]}` sha256 `{C.PLAN_SHA256}`" in dec:
        assert probs == []
    else:
        assert probs and all("not pinned" in p for p in probs)


# ------------------------------------------------------------------------------------------------ Q-108's reused code


def test_q108s_constructions_reproduced_where_reused(C):
    """On one toy null of each kind and the same entropy, this runner's scope-Q counts are Q-108's (`run_mc`,
    `run_exact`), and its scope-D counts at most Q-108's (the balance limit only removes)."""
    Q = pristine_q108()
    p, days = synthetic_pairs(n_judged=130, per_session=10, sub=60)
    n = len(days)
    seeds = toy_seeds(C)
    plan = {x["null"]: x for x in C.core_plan(seeds)}
    inp = C.CAL.Inputs(p, n, seeds)
    shared = ["cons", "cons_m1.25", "cons_m1.5", "cons_bm_m1.25"]
    for name in ("fixed:offered:win1:flip21", "fixed:taken:net3:coin", "sub:1000:000:win1:markov30",
                 "syn:cluster:1000"):
        e = plan[name]
        ds = inp.data_for(e) if e["group"] != "synthetic" else None
        a = C.run_mc(e, C.CAL.mc_generator(e, inp), ds, 300, 300, n, shared)
        b = Q.run_mc(e, Q.mc_generator(e, inp), ds, 300, 300, n, shared, None)
        for c in shared:
            assert np.array_equal(a["counts"][(c, "Q")], b["counts"][(c, "Q")]), (name, c)
            assert (a["counts"][(c, "D")] <= b["counts"][(c, "D")]).all()
        assert a["mismatches"] == [] and b["mismatches"] == []
    for name in ("fixed:offered:win1:flip42", "sub:1000:000:net3:alt45"):
        e = plan[name]
        ds = inp.data_for(e)
        a = C.run_exact(e, ds.V, ds.N, n, shared, ds=ds)
        b = Q.run_exact(e, ds, n, shared, None)
        for c in shared:
            assert np.array_equal(a["counts"][(c, "Q")], b["counts"][(c, "Q")]), (name, c)
            assert (a["counts"][(c, "D")] <= b["counts"][(c, "D")]).all()
        assert a["mismatches"] == []


def test_the_sizing_nulls_redecide_their_first_five_rejecting_cells(C):
    """The plan's 4.1: on a sizing null the first 5 rejecting cells per candidate and scope are re-decided by the
    scalar form at every k, and no uniform cells; on a core exact null the first 100 and the 20 uniform cells."""
    from types import SimpleNamespace

    n = 300
    g = np.random.default_rng([SEED, 90])
    N = g.poisson(6, n).astype(float)
    s = np.repeat(np.arange(n), N.astype(int))
    x = g.choice([-0.5, 0.0, 0.5], len(s), p=[0.12, 0.5, 0.38])
    V = np.bincount(s, weights=x, minlength=n)
    ds = SimpleNamespace(s=s)
    cands = ["cons", "cons_m1.5"]
    e = {"null": "toy", "model": "flip42", "sample_entropy": None}
    res = C.run_exact(e, V, N, n, cands, ds=ds, n_first=5, uniform=False)
    rej = {k: int(v[0] > 0) for k, v in res["counts"].items()}
    assert sum(rej.values()) >= 1, "a toy with no rejection checks nothing"
    ex = C.L2.exact_flip2(V, N, 42, cands=cands, n_first=5)
    want = sum(len(v) for v in ex.samples.values()) * 8
    assert res["checked"] == want > 0 and res["mismatches"] == []
    assert all(len(v) <= 5 for v in ex.samples.values())
    e2 = dict(e, sample_entropy=[TOY, 0])
    res2 = C.run_exact(e2, V, N, n, cands, ds=ds, n_first=100, uniform=True)
    assert res2["checked"] > res["checked"] and res2["mismatches"] == []


# ------------------------------------------------------------------------------------------------ end to end


def toy_grid(C, monkeypatch):
    monkeypatch.setattr(C, "SIZES", (200, 1000))
    monkeypatch.setattr(C, "PARTS", ("core", "sizing200", "sizing1000", "probe", "drift", "choice"))
    monkeypatch.setattr(C, "N_CORE", 1)
    monkeypatch.setattr(C, "N_SUBSETS", 3)
    monkeypatch.setattr(C, "N_NONPERSISTENT", 1)
    monkeypatch.setattr(C, "PROBE_PER_SIZE", 1)
    monkeypatch.setattr(C, "CP_ONE", C.CP_ONE[:1] + C.CP_ONE[-1:])
    monkeypatch.setattr(C, "FLAT_L", (21,))
    monkeypatch.setattr(C, "DRIFT_SCENARIOS", ((0, "A", 500, 100, 0.0, False), (1, "B", 500, 100, 0.05, True)))
    monkeypatch.setattr(C, "DRIFT_POPULATIONS", 1)


def test_a_small_end_to_end_calibration_writes_nothing(C, monkeypatch, tmp_path):
    """Toy streams on a 130-session calendar, the grid shrunk (two sizes, one core and two sizing subsets each, one
    probed subset a size, two count-persistent and one `flat` null, two drift populations): every part, every
    candidate, both scopes, the re-decision, the probe on the ranking, the choice -- and no file written in the tree."""
    before = {p for p in (ROOT / "results").rglob("*")} if (ROOT / "results").is_dir() else set()
    monkeypatch.chdir(tmp_path)
    toy_grid(C, monkeypatch)
    p, days = synthetic_pairs(n_judged=130, per_session=10, sub=70)
    n = len(days)
    seeds = toy_seeds(C)
    block = set(seeds.values())
    work = tmp_path / "work"
    inp = C.CAL.Inputs(p, n, seeds)
    cands = list(C.CANDS)
    parts = {}
    for part in ("core", "sizing200", "sizing1000"):
        plan = C.core_plan(seeds) if part == "core" else C.sizing_plan(seeds, int(part[6:]))
        assert C.provenance_problems(plan, seeds, block) == []
        out = C.compute_nulls(part, plan, inp, n, 200, cands, reps_beside=150, log=lambda m: None)
        assert not C.failed(out), (part, out["mismatches"][:2], out["nesting"][:2])
        C.write_part(work, part, out, {"commit": "toy", "seed_map": seeds, "versions": {}})
        parts[part] = C.read_part_frames(work, part)
    sz = pd.concat([parts["sizing200"]["size"], parts["sizing1000"]["size"]], ignore_index=True)
    ranking = C.L2.probe_ranking(C.ranking_scores(sz), per_size=1, core=1)
    assert set(ranking) == {200, 1000} and all(len(v) == 1 for v in ranking.values())
    plan = C.probe_plan(seeds, ranking)
    assert len(plan) == 2 * 2 * 4 and C.provenance_problems(plan, seeds, block) == []
    out = C.compute_nulls("probe", plan, inp, n, 200, cands, log=lambda m: None)
    out["ranking"] = C.ranking_frame(ranking)
    assert not C.failed(out)
    C.write_part(work, "probe", out, {"commit": "toy", "seed_map": seeds, "versions": {}})
    parts["probe"] = C.read_part_frames(work, "probe")
    plan = C.drift_plan(seeds)
    assert len(plan) == 10 and C.provenance_problems(plan, seeds, block) == []
    out = C.compute_nulls("drift", plan, None, n, 200, cands, drift_inputs=C.drift_inputs_for(n), log=lambda m: None)
    assert not C.failed(out)
    C.write_part(work, "drift", out, {"commit": "toy", "seed_map": seeds, "versions": {}})
    parts["drift"] = C.read_part_frames(work, "drift")
    checked = {k: v["manifest"]["meta"]["scalar_checked"] for k, v in parts.items()}
    assert checked["core"] > 1000 and checked["probe"] > 0, checked                      # sizing: no rejection here
    assert checked["drift"] == 0                                                         # beside: not re-decided
    res = C.choice_tables(parts, seeds)
    assert res["failed"] == [], res["failed"]
    fr = res["frames"]
    assert set(fr) == set(C.RESULT_FILES)
    size = res["size"]
    assert set(size["scope"]) == {"Q", "D"} and set(size["candidate"]) == set(C.CANDS)
    assert (size[size["model"] == "flip63"]["admitted"] == 0).all()                       # never admitted at 63
    assert len(fr["q126_cal_sizing"]) == 2 * 2 * 2 * 5 and "count|cons_m2|D|k20" in fr["q126_cal_sizing"]
    assert len(fr["q126_cal_drift"]) == 10
    line = res["choice"]["line"]
    assert line == "NONE" or line.startswith("CHOSEN ")
    elig = res["elig"]
    assert len(elig) == 16 and {"p_mc", "bad_subsets", "probe_worst_share", "worst_exact_ratio_core"} <= set(elig)
    assert (elig["subsets"] == 2 * 3).all()                                                # the toy's 3 subsets a size
    ch = fr["q126_choice"]
    assert (ch["row"] == "decision").sum() == 1 and (ch["row"] == "probe_ranking").sum() == 2
    assert (ch["row"] == "floor_emptied_branch").sum() == 2
    assert np.isfinite(res["psum"]["P"].astype(float)).all()
    # a planted change to the probe's ranking is a failed check
    bad = dict(parts)
    bad["probe"] = dict(parts["probe"], ranking=parts["probe"]["ranking"].assign(j=lambda d: d["j"] + 1))
    assert C.choice_tables(bad, seeds)["failed"]
    # a missing part is NOT CHECKED
    assert "NOT CHECKED" in C.choice_tables({k: v for k, v in parts.items() if k != "drift"}, seeds)["failed"][0]
    after = {p for p in (ROOT / "results").rglob("*")} if (ROOT / "results").is_dir() else set()
    assert after == before
    assert sorted(x.name for x in tmp_path.iterdir()) == ["work"]


def load_validate():
    name = "q126_validate_for_cal_t"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / "q126_validate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
