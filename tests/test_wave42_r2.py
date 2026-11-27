"""W42-R2 (`docs/plans/WAVE42_SETTING_RULE_R2.md`, `extended/wave42_r2.py`, `scripts/wave42_r2_apply.py`): W42-R1 with
one added limit, a floor on the median 12-month net cash. Synthetic readings only (W42-R1's tests' generator), no bar,
no result file of this repository, no held-out outcome:

- **W42-R1 unchanged with the limit off**: the same output, digest for digest; W42-R1's module untouched; W42-R1's own
  code objects run;
- **only the stated keys move with it on**; every limit keeps W42-R1's estimates, and its value moves only through
  the headroom (z at L = 7, and E-296's corrected error term) where the headroom binds;
- **the corrected headroom** (`headroom`, `limit_value`): by hand; fed W42-R1's error term, the selection reproduces
  W42-R1's limits exactly; and a simulation in which W42-R1's term falsely refuses a design equal to the best baseline
  well above nominal while the corrected one is at nominal;
- **the floor's value comes from the formula** (recomputed here by the text's words), moves with the baselines, and
  no number is typed in its definition;
- **the binding, the refusals, the vacuity re-read and the r2 block**;
- **the application** on synthetic files in a temporary folder;
- **the power check** (`tests/w42r2_power.py`) at a reduced count.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import importlib.util
import json
import math
import re
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from scipy import stats

from extended import h4_audit as HA
from extended import wave42 as R
from extended import wave42_r2 as R2

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "plans" / "WAVE42_SETTING_RULE_R2.md"
MODULE = ROOT / "extended" / "wave42_r2.py"


def _load(name: str, rel: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod                               # a dataclass looks its module up by name
    spec.loader.exec_module(mod)
    return mod


T = _load("wave42_rule_generator", "tests/test_wave42_rule.py")      # W42-R1's tests' synthetic generator
AP = _load("wave42_r2_apply_under_test", "scripts/wave42_r2_apply.py")
PW = _load("w42r2_power_under_test", "tests/w42r2_power.py")
UNITS = {b: "d" * 64 for b in R.BASELINES}                # a synthetic units-file sha256 per baseline
ENTROPY = int.from_bytes(hashlib.sha256(b"tests/test_wave42_r2.py synthetic net_month_12").digest()[:16], "big")


def _net12(rs, law=(2.0, 20.0), stream: int = 0, shared: bool = False):
    """W42-R1's synthetic readings with `net_month_12` added (normal per unit, in fee units; blank off E_252)."""
    sl = T._sl(rs[R.BASELINES[0]].starts)
    kids = np.random.SeedSequence(ENTROPY, spawn_key=(stream,)).spawn(len(R.BASELINES))
    out = {}
    for i, b in enumerate(R.BASELINES):
        r = rs[b]
        mu, sd = law if isinstance(law, tuple) else law[i]
        x = T.FEE * np.random.default_rng(kids[0 if shared else i]).normal(mu, sd, (len(r.starts), len(r.seeds)))
        x[sl < R2.YEAR] = np.nan
        out[b] = R.BaselineReading(r.name, r.block, r.reading, r.starts, r.seeds, {**dict(r.values), R2.NET12_KEY: x})
    return out


def _r2(rx, base, *, h4=None, src=UNITS, **kw):
    return R2.setting_rule(rx, h4=h4 if h4 is not None else T._bind(base), search_calendar=T.CAL, fee_unit=T.FEE,
                           fee_source=R.FEE_SOURCE, test_starts=T.TEST_STARTS, test_starts_source=T.SRC,
                           net12_source=src, **kw)


@pytest.fixture(scope="module")
def pair():
    rs = T._readings()
    rx = _net12(rs, law=[(2.0, 20.0), (4.0, 20.0), (6.0, 20.0), (8.0, 20.0)])
    return SimpleNamespace(rs=rs, rx=rx, r1=T._run(rs), r2=_r2(rx, rs))


def _net(values) -> dict:
    return next(x for x in values["limits"]["values"] if x["name"] == R2.NET12_LIMIT.name)


# ------------------------------------------------------------------------------------- W42-R1 unchanged with it off
def test_with_the_limit_off_w42_r2_returns_w42_r1s_output_exactly(pair) -> None:
    before = (R.LIMITS, dict(R.REQUIRED), R.RULE_ID, R.OUTPUT_NAME, R.HORIZONS, dict(R.CONSTANTS))
    off = R2.setting_rule(pair.rs, h4=T._bind(pair.rs), search_calendar=T.CAL, fee_unit=T.FEE,
                          fee_source=R.FEE_SOURCE, test_starts=T.TEST_STARTS, test_starts_source=T.SRC,
                          net_floor=False)
    assert off.digest() == pair.r1.digest() and off.as_json() == pair.r1.as_json()
    _r2(pair.rx, pair.rs)                                  # a W42-R2 call leaves W42-R1's module as it was
    assert (R.LIMITS, dict(R.REQUIRED), R.RULE_ID, R.OUTPUT_NAME, R.HORIZONS, dict(R.CONSTANTS)) == before
    assert len(R.LIMITS) == 6 and R2.NET12_KEY not in R.REQUIRED
    assert T._run(pair.rs).digest() == pair.r1.digest()


def test_the_rebound_functions_are_w42_r1s_own_code() -> None:
    ns = R2.namespace()
    fns = [k for k, v in vars(R).items() if callable(v) and getattr(v, "__globals__", None) is vars(R)]
    assert "setting_rule" in fns and "limit_estimate" in fns and "_validate" in fns
    for k in fns:
        assert ns[k].__code__ is getattr(R, k).__code__, k
        assert ns[k].__globals__ is ns and ns[k] is not getattr(R, k), k
    assert ns["LIMITS"] is R2.LIMITS and ns["REQUIRED"] is R2.REQUIRED and ns["RULE_ID"] == "W42-R2"
    assert set(R2.tables()) == set(R2.OVERRIDES) == set(R2.tables(False))
    with pytest.raises(KeyError, match="an override replaces an existing table only"):
        R2.rebind(R, {"NO_SUCH_TABLE": 1})


def test_a_monkeypatched_w42_r1_table_reaches_w42_r2(monkeypatch) -> None:
    """The namespace is copied at each call, so W42-R1's module as it is at the call is the one read."""
    monkeypatch.setattr(R, "HELD_OUT_CALENDAR_SHA256", "9" * 64)
    assert R2.namespace()["HELD_OUT_CALENDAR_SHA256"] == "9" * 64


# --------------------------------------------------------------------------------- only the stated keys move
MOVING = {"rule_id", "constants", "application", "limits", "h4", "input_sha256", "r2", "inactivity_guards"}


def _se(x: dict) -> float:
    """E-296's error term from a limit's own record: sqrt(se_test^2 + (sd_best / sqrt(J_H4))^2)."""
    return math.sqrt(x["best_se_test"] ** 2 + x["best_se_search"] ** 2)


def test_with_the_limit_on_only_the_stated_keys_move(pair) -> None:
    a, b = pair.r1.values, pair.r2.values
    assert set(b) == set(a) | {"r2"}
    for k in sorted(set(a) - MOVING):
        assert json.dumps(a[k], sort_keys=True) == json.dumps(b[k], sort_keys=True), k
    assert b["rule_id"] == "W42-R2" and b["constants"] == R2.CONSTANTS
    assert b["application"]["script"] == "scripts/wave42_r2_apply.py" and b["application"]["output"] == R2.OUTPUT_NAME
    assert {k: v for k, v in b["h4"].items() if k not in ("readings_sha256", "collection_readings_sha256")} == \
        {k: v for k, v in a["h4"].items() if k != "readings_sha256"}
    assert b["h4"]["collection_readings_sha256"] == a["h4"]["readings_sha256"] == R.readings_digest(pair.rs)
    assert b["h4"]["readings_sha256"] == R.readings_digest(pair.rx)
    assert b["limits"]["limits_set"] == 7 and a["limits"]["limits_set"] == 6
    assert b["limits"]["headroom_z"] == pytest.approx(stats.norm.ppf(1 - (1 - R.POWER_TARGET) / 7), abs=1e-12)
    assert b["inactivity_guards"]["not_paid_within_B"] == ("live" if not next(
        x for x in b["limits"]["values"] if x["name"] == "not_paid_within_B")["vacuous"] else
        "vacuous: only CHARTER 3.8 (c)'s long-run gate stops a quitter")
    assert b["limits"]["headroom_form"] == R2.HEADROOM_FORM and b["limits"]["h4_seeds"] == T.J0
    la = {x["name"]: x for x in a["limits"]["values"]}
    lb = {x["name"]: x for x in b["limits"]["values"]}
    assert list(lb) == [L.name for L in R.LIMITS] + [R2.NET12_LIMIT.name]
    for name, y in lb.items():
        h = int(y["horizon"])
        r_t = math.sqrt(b["search_starts"][str(h)] / (R.TEST_SEEDS * T.TEST_STARTS[h]))
        assert y["best_sd_per_seed"] == y["sd_per_seed"][y["best"]]                  # W42-R1's own sd_best
        assert y["best_se_test"] == pytest.approx(y["sd_star"] * r_t, rel=1e-12)    # the test term at sd*
        if name in la:
            for k in ("baseline_values", "best", "worst", "by_search_year", "direction", "stat"):
                assert la[name][k] == y[k], (name, k)
            assert la[name]["best_se_test"] == pytest.approx(y["best_sd_per_seed"] * r_t, rel=1e-12)  # W42-R1's
        assert y["headroom_z"] == b["limits"]["headroom_z"]
        assert y["sd_star"] == max(y["sd_per_seed"].values()) == y["sd_per_seed"][y["sd_star_baseline"]]
        assert y["best_se_search"] == pytest.approx(y["sd_star"] / math.sqrt(T.J0), rel=1e-12)
        assert y["headroom_se"] == pytest.approx(_se(y), rel=1e-12)
        sign = 1.0 if y["direction"] == "ceiling" else -1.0
        mb = y["baseline_values"][y["best"]]
        assert y["headroom_needed"] == pytest.approx(mb + sign * y["headroom_z"] * y["headroom_se"], rel=1e-12)
        assert y["headroom_needed_w42_r1"] == pytest.approx(mb + sign * y["headroom_z"] * y["best_sd_per_seed"] * r_t,
                                                            rel=1e-12)
        if y["binds"] == "worst_baseline":
            assert y["value"] == y["baseline_values"][y["worst"]]
        else:
            assert y["value"] == y["headroom_needed"]
        for bl, c in y["baseline_checks"].items():               # re-read at the corrected value
            assert c["estimate"] == y["baseline_values"][bl]
            assert c["inside"] is bool((c["estimate"] - y["value"]) * sign <= 0)


def test_a_headroom_bound_w42_r1_limit_moves_out_by_z_at_seven_and_nothing_else_does() -> None:
    rs = T._readings()
    same = np.asarray(rs["p14"].values["taken_mean"], dtype=float)
    for b in R.BASELINES:                                  # every baseline equal on taken_mean: the headroom binds
        rs = T._with(rs, b, "taken_mean", lambda _x: same.copy())
    rx = _net12(rs)
    a, b = T._run(rs).values, _r2(rx, rs).values
    x = next(v for v in a["limits"]["values"] if v["name"] == "taken_mean_p10")
    y = next(v for v in b["limits"]["values"] if v["name"] == "taken_mean_p10")
    assert x["binds"] == y["binds"] == y["binds_w42_r1_headroom"] == "headroom"
    m = x["baseline_values"][x["best"]]
    assert x["value"] == pytest.approx(m - R.limit_z(6) * x["best_se_test"], rel=1e-12)          # W42-R1, L = 6
    assert y["value_w42_r1_headroom"] == pytest.approx(m - R.limit_z(7) * x["best_se_test"], rel=1e-12)
    assert y["sd_star"] == y["best_sd_per_seed"]                         # one matrix for all four: equal sds
    se = math.sqrt(x["best_se_test"] ** 2 + y["sd_star"] ** 2 / T.J0)                             # E-296
    assert y["value"] == pytest.approx(m - R.limit_z(7) * se, rel=1e-12)
    assert y["value"] < y["value_w42_r1_headroom"] < x["value"]          # a floor: further out is lower


# ------------------------------------------------------------------------------- the value comes from the formula
def _formula(rx, J=R.TEST_SEEDS):
    """Sections 3.2 and 4.2 by their words, independently of the module: the median of the pooled units of E_252,
    sd* the largest of the four baselines' per-seed sds, the two terms at it, z at L = 7, the floor; and W42-R1's
    value beside (the test term only, at the drawn winner's sd)."""
    sl = T._sl(rx[R.BASELINES[0]].starts)
    e = sl >= 252
    X = {b: np.asarray(rx[b].values["net_month_12"], dtype=float)[e] for b in R.BASELINES}
    M = {b: float(np.quantile(X[b].ravel(), 0.5)) for b in R.BASELINES}
    best = max(R.BASELINES, key=lambda b: (M[b], -R.BASELINES.index(b)))
    worst = min(R.BASELINES, key=lambda b: (M[b], R.BASELINES.index(b)))
    nJ = X[best].shape[1]
    sds = {b: float(np.std([np.quantile(X[b][:, c], 0.5) for c in range(nJ)], ddof=1)) for b in R.BASELINES}
    sd = max(sds.values())
    r_t = math.sqrt(int(e.sum()) / (J * T.TEST_STARTS[252]))
    se_test = sd * r_t
    se = math.sqrt(se_test ** 2 + sd ** 2 / nJ)                       # E-296: M_best's own noise beside
    z = float(stats.norm.ppf(1.0 - (1.0 - 0.8) / 7))
    need, need_old = M[best] - z * se, M[best] - z * sds[best] * r_t
    return {"M": M, "best": best, "worst": worst, "se_test": se_test, "se": se, "sds": sds, "sd_star": sd,
            "value": min(M[worst], need), "value_old": min(M[worst], need_old),
            "binds": "worst_baseline" if M[worst] <= need else "headroom"}


def test_the_floors_value_is_w42_r1s_formula_recomputed_from_the_readings(pair) -> None:
    f, net = _formula(pair.rx), _net(pair.r2.values)
    assert net["value"] == pytest.approx(f["value"], rel=1e-12)
    assert net["binds"] == f["binds"] and net["best"] == f["best"] and net["worst"] == f["worst"]
    assert net["best_se_test"] == pytest.approx(f["se_test"], rel=1e-12)
    assert net["headroom_se"] == pytest.approx(f["se"], rel=1e-12)
    assert net["sd_star"] == pytest.approx(f["sd_star"], rel=1e-12)
    for b in R.BASELINES:
        assert net["sd_per_seed"][b] == pytest.approx(f["sds"][b], rel=1e-12)
    assert net["value_w42_r1_headroom"] == pytest.approx(f["value_old"], rel=1e-12)
    for b in R.BASELINES:
        assert net["baseline_values"][b] == pytest.approx(f["M"][b], rel=1e-12)
    assert net["direction"] == "floor" and net["stat"] == "p50" and net["horizon"] == 252 and net["key"] == "net_month_12"
    assert pair.r2.values["r2"]["value"] == net["value"]


def test_identical_baselines_put_the_floor_at_the_headroom() -> None:
    rs = T._readings()
    rx = _net12(rs, shared=True)
    f, net = _formula(rx), _net(_r2(rx, rs).values)
    assert f["binds"] == net["binds"] == "headroom"
    assert net["value"] == pytest.approx(f["value"], rel=1e-12)
    assert net["value_w42_r1_headroom"] == pytest.approx(f["value_old"], rel=1e-12) and net["value"] < f["value_old"]


def test_the_floor_moves_with_the_baselines_and_with_nothing_typed(pair) -> None:
    v0 = _net(pair.r2.values)["value"]
    c, k = 3.0 * T.FEE, 2.0
    for fn, want in ((lambda x: x + c, v0 + c), (lambda x: x * k, v0 * k)):
        rx = pair.rx
        for b in R.BASELINES:
            rx = T._with(rx, b, "net_month_12", fn)
        assert _net(_r2(rx, pair.rs).values)["value"] == pytest.approx(want, rel=1e-9)


def test_no_number_is_typed_in_the_added_limits_definition() -> None:
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "NET12_LIMIT" for t in n.targets))
    assert not [n for n in ast.walk(node) if isinstance(n, ast.Constant) and type(n.value) in (int, float)]
    assert "value" not in {f.name for f in R.LimitSpec.__dataclass_fields__.values()}
    assert R2.YEAR == 12 * R.MONTH == 252 and R2.LIMITS == R.LIMITS + (R2.NET12_LIMIT,)
    assert R2.REQUIRED == {**R.REQUIRED, "net_month_12": (252, -math.inf, math.inf)}
    assert R2.REQUIRED["net_month_12"][1:] == R.REQUIRED["net_month_1"][1:]


# ------------------------------------------------------------------------------- the corrected headroom (E-296)
def test_the_headroom_by_hand() -> None:
    h = R2.headroom(10.0, 2.0, 400, 100, 1000, 100, 1.5, "ceiling")
    se_t, se_s = 2.0 * math.sqrt(400 / (1000 * 100)), 2.0 / 10.0
    assert h["se_test"] == pytest.approx(se_t) and h["se_search"] == pytest.approx(se_s)
    assert h["se"] == pytest.approx(math.hypot(se_t, se_s))
    assert h["needed"] == pytest.approx(10.0 + 1.5 * math.hypot(se_t, se_s))
    assert set(h) == {"se_test", "se_search", "se", "needed"}
    f = R2.headroom(10.0, 2.0, 400, 100, 1000, 100, 1.5, "floor")
    assert f["needed"] == pytest.approx(10.0 - 1.5 * math.hypot(se_t, se_s))
    assert R2.headroom(10.0, 0.0, 400, 100, 1000, 100, 1.5, "floor")["needed"] == 10.0
    for bad in (dict(direction="both"), dict(j_h4=0), dict(sd=-1.0), dict(sd=math.nan)):
        kw = dict(m_best=1.0, sd=1.0, n_search=1, n_test=1, j_test=1, j_h4=1, z=1.0, direction="floor")
        kw.update(bad)
        with pytest.raises(ValueError):
            R2.headroom(**kw)


def test_limit_value_fed_w42_r1s_error_term_reproduces_w42_r1s_limits(pair) -> None:
    """W42-R1's section 6 steps 3-4 re-written in `limit_value`: fed W42-R1's own needed value, it gives W42-R1's
    value, binds and vacuity for each of its six limits (the counts' a priori end included)."""
    a = pair.r1.values
    sl = T._sl()
    B = float(a["budgets"]["primary"])
    per = {b: R.unit_values(pair.rs[b].values, B) for b in R.BASELINES}
    kinds = {L.name: L for L in R.LIMITS}
    for x in a["limits"]["values"]:
        L = kinds[x["name"]]
        pooled = np.concatenate([per[b][L.key][sl >= L.horizon].ravel() for b in R.BASELINES])
        got = R2.limit_value(L.direction, L.kind, x["baseline_values"][x["worst"]], x["headroom_needed"], pooled)
        assert got == {"value": x["value"], "binds": x["binds"], "vacuous": x["vacuous"],
                       "vacuous_reason": x["vacuous_reason"]}, x["name"]
    p = np.asarray([1.0, 2.0, 3.0])
    assert R2.limit_value("floor", "count", 0.5, -1.0, p)["vacuous_reason"].startswith("at or beyond")
    assert R2.limit_value("floor", R2.NET12_KIND, -2.0, -1.0, p)["vacuous_reason"].startswith("beyond every")
    assert R2.limit_value("floor", R2.NET12_KIND, 1.5, 1.0, p) == {"value": 1.0, "binds": "headroom",
                                                                    "vacuous": True, "vacuous_reason": R2._VACUOUS_UNITS}
    assert R2.limit_value("ceiling", "share", 1.0, 0.5, p)["vacuous_reason"].startswith("at or beyond")
    assert R2.limit_value("ceiling", "days", 2.0, 2.0, p)["binds"] == "worst_baseline"      # a tie is the worst's


def test_the_old_headroom_falsely_refuses_and_the_corrected_one_is_at_nominal() -> None:
    """A design equal to the best baseline, where the headroom binds (the best is the only baseline: M_best is the
    pooled mean of H4's search units). W42-R1's term counts the test's coin noise only, so the design is refused well
    above the nominal 1 - Phi(z_7); E-296's term counts M_best's own noise too, and the refusal is at nominal."""
    rng = np.random.default_rng(np.random.SeedSequence(ENTROPY, spawn_key=(1,)))
    n_s, n_t, J, nJ = 40, 40, R.TEST_SEEDS, HA.H4_J
    z = R.limit_z(7)
    old = new = 0
    reps = 0
    for _ in range(10):
        X = rng.normal(0.0, 1.0, (2000, n_s, nJ))                    # 2000 search draws of n_s starts x nJ seeds
        cols = X.mean(axis=1)                                         # each seed's statistic (the mean)
        M, sd = cols.mean(axis=1), cols.std(axis=1, ddof=1)
        D = rng.normal(0.0, 1.0 / math.sqrt(n_t * J), 2000)          # the design's held-out estimate, exactly normal
        for m, s_, d in zip(M, sd, D):
            h = R2.headroom(float(m), float(s_), n_s, n_t, J, nJ, z, "floor")
            old += int(d < float(m) - z * h["se_test"])
            new += int(d < h["needed"])
        reps += 2000
    nominal = float(stats.norm.sf(z))
    ratio = math.sqrt(n_s / (J * n_t)) / math.hypot(math.sqrt(n_s / (J * n_t)), 1 / math.sqrt(nJ))
    predicted_old = float(stats.norm.sf(z * ratio))
    tol = 5 * math.sqrt(nominal * (1 - nominal) / reps)
    assert abs(new / reps - nominal) < tol, (new / reps, nominal)
    assert abs(old / reps - predicted_old) < 5 * math.sqrt(predicted_old * (1 - predicted_old) / reps)
    assert old / reps > 5 * nominal


def test_sd_star_is_the_largest_of_the_four_baselines_not_the_winners() -> None:
    """B-1: a non-winner much noisier on net_month_12 (the naive coin, lowest median) supplies sd*; the headroom's
    terms are at it, not at the winner's (p16's) sd."""
    rs = T._readings()
    rx = _net12(rs, law=[(3.9, 80.0), (4.0, 20.0), (4.0, 20.0), (4.05, 20.0)])
    net = _net(_r2(rx, rs).values)
    assert net["sd_star_baseline"] == "naive_coin" != net["best"]
    assert net["sd_star"] == net["sd_per_seed"]["naive_coin"] > 2 * net["sd_per_seed"][net["best"]]
    n_s = int((T._sl() >= 252).sum())
    assert net["best_se_search"] == pytest.approx(net["sd_star"] / math.sqrt(T.J0), rel=1e-12)
    assert net["best_se_test"] == pytest.approx(net["sd_star"] * math.sqrt(n_s / (R.TEST_SEEDS * T.TEST_STARTS[252])),
                                                rel=1e-12)
    f = _formula(rx)
    assert net["value"] == pytest.approx(f["value"], rel=1e-12) and f["sd_star"] == pytest.approx(net["sd_star"])


def _rt_config(reps: int, kind: int):
    """The red team's scenario in the Gaussian form of section 7.2: four tied, the first eight times noisier,
    independent search noise, the design equal to the noisy first; the real counts."""
    c = PW.counts()
    n_s, n_t, j_h4, J = c["n_s_252"], c["n_t_252"], c["j_h4"], c["j_test"]
    r_t = n_s / (J * n_t)
    s = np.asarray([8.0, 1.0, 1.0, 1.0])
    rng = np.random.default_rng(np.random.SeedSequence(ENTROPY, spawn_key=(2, kind)))
    M = s / math.sqrt(j_h4) * rng.standard_normal((reps, 4))
    sd_hat = s * np.sqrt(rng.chisquare(j_h4 - 1, (reps, 4)) / (j_h4 - 1))
    D = s[0] * math.sqrt(r_t) * rng.standard_normal(reps)
    return M, sd_hat, D, r_t, j_h4, n_s, n_t, J


def test_the_red_teams_scenario_holds_c1_under_sd_star_and_fails_under_the_old_forms() -> None:
    reps = 200000
    M, sd_hat, D, r_t, j_h4, *_ = _rt_config(reps, 0)
    v = PW.config_values(M, sd_hat, r_t, j_h4, PW.Z7)
    p = {f: float(np.mean(D < v[f])) for f in PW.FORMS}
    bound = PW.c1_bound(PW.T_SELECTION, n=reps)
    assert p["sd_star"] <= bound, (p, bound)
    assert p["winner"] > bound and p["w42_r1"] > bound, (p, bound)


def test_the_vectorised_form_equals_headroom_and_limit_value() -> None:
    M, sd_hat, D, r_t, j_h4, n_s, n_t, J = _rt_config(300, 1)
    v = PW.config_values(M, sd_hat, r_t, j_h4, PW.Z7)
    for i in range(M.shape[0]):
        b, w = PW.best_worst("floor", list(M[i]))
        for f in PW.FORMS:
            want = PW.form_value(f, "floor", M[i, b], M[i, w], list(sd_hat[i]), b, n_s, n_t, J, j_h4, PW.Z7)
            assert v[f][i] == pytest.approx(want, rel=1e-9, abs=1e-12), (i, f)


def test_the_beside_block_reads_nominal_at_the_held_out_read_and_more_at_f13s_sizes(pair) -> None:
    for x in pair.r2.values["limits"]["values"]:
        bs = x["beside"]
        assert bs["refusal_at_read"]["held_out"] == pytest.approx(float(stats.norm.sf(x["headroom_z"])), rel=1e-12)
        assert bs["refusal_at_read"]["f13_screen"] > bs["refusal_at_read"]["f13_deciding"] > \
            bs["refusal_at_read"]["held_out"]
        lo, hi = bs["sd_star_interval"]
        assert lo <= x["sd_star"] <= hi and bs["sd_star_interval_level"] == 0.95
        assert bs["decides"].startswith("nothing")
    n_s, n_t, j, jh = 800, 400, 1000, 128
    assert R2.refusal_at_read(2.0, n_s, n_t, j, jh, n_t, j) == pytest.approx(float(stats.norm.sf(2.0)))
    held, read = math.sqrt(n_s / (j * n_t) + 1 / jh), math.sqrt(n_s / (16 * n_s) + 1 / jh)
    assert R2.refusal_at_read(2.0, n_s, n_t, j, jh, n_s, 16) == pytest.approx(float(stats.norm.sf(2.0 * held / read)))
    lo, hi = R2.sd_interval(1.0, jh)
    k = jh - 1
    assert lo == pytest.approx(math.sqrt(k / stats.chi2.ppf(0.975, k))) and hi == pytest.approx(
        math.sqrt(k / stats.chi2.ppf(0.025, k)))
    assert R2.READS_BESIDE == {"f13_screen": (4, 4), "f13_deciding": (16, 1)}


def test_the_namespace_is_built_once_and_again_after_a_change(monkeypatch) -> None:
    a = R2.namespace()
    assert R2.namespace() is a and R2.namespace(False) is R2.namespace(False) and R2.namespace(False) is not a
    monkeypatch.setattr(R, "HELD_OUT_CALENDAR_SHA256", "8" * 64)
    b = R2.namespace()
    assert b is not a and b["HELD_OUT_CALENDAR_SHA256"] == "8" * 64
    monkeypatch.undo()
    c = R2.namespace()
    assert c["HELD_OUT_CALENDAR_SHA256"] == R.HELD_OUT_CALENDAR_SHA256 != "8" * 64


def test_the_criteria_functions() -> None:
    assert PW.P0 == pytest.approx((1 - R.POWER_TARGET) / 7)
    assert PW.c1_bound(1.4, n=4000) == pytest.approx(1.4 * PW.P0 + 3 * math.sqrt(1.4 * PW.P0 * (1 - 1.4 * PW.P0) / 4000))
    assert PW.c1_bound(1.0, se=0.01) == pytest.approx(PW.P0 + 0.03)
    assert PW.cluster_se([0.0, 1.0, 0.0, 1.0]) == pytest.approx(float(np.std([0, 1, 0, 1], ddof=1)) / 2)
    rows = [{"all": {f: k for f in PW.FORMS}, "limit": {"a": {f: k for f in PW.FORMS}}, "headroom": {"a": True}}
            for k in (4, 3, 4, 4)]
    agg = PW.aggregate_joint([{"held_out_draws": 4, "per_draw": rows}])
    assert agg["joint_pass"]["sd_star"] == pytest.approx(15 / 16)
    assert agg["c2_bound"]["sd_star"] == pytest.approx(R.POWER_TARGET - 3 * PW.cluster_se([1, 0.75, 1, 1]))
    assert agg["limits"]["a"]["sd_star"]["refusal"] == pytest.approx(1 / 16)
    low = [{"all": {f: 0 for f in PW.FORMS}, "limit": {"a": {f: 0 for f in PW.FORMS}}, "headroom": {"a": True}}] * 20
    bad = PW.aggregate_joint([{"held_out_draws": 4, "per_draw": rows + low}])
    assert not bad["c2_pass"]["sd_star"] and not bad["c1_pass"]["sd_star"] and bad["c6_fails_under_old"]


def test_the_declaration_records_the_read_before_the_form_and_its_corrections() -> None:
    text = DOC.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "was ruled (Q-221) after the early look had shown P-14's H4-B search-year readings of that very statistic" in flat
    assert "E-291" in flat and "journey_measures.YEAR" in flat and "CHARTER 2's objective" in flat
    assert "F-13's finalists are shown with and without the floor" in flat
    assert "E-015" not in text                                          # m-3: not E-015 (3)
    assert "by the rule's intent** (W42-R1 section 6, step 3" in flat   # m-4
    assert "The nominal rate of section 4 holds at the held-out read only" in flat   # m-1
    assert "**It is stated and not propagated**" in flat                # m-2
    assert "Q-189 and DRAFT_F-13 must name `scripts/wave42_r2_apply.py`" in flat       # m-5
    assert "built once per process" in flat                             # m-6
    for c in ("C1", "C2", "C3", "C4", "C5", "C6"):
        assert f"**{c}," in flat, c


# ------------------------------------------------------------------------------------------- the document's tables
def _table(tag: str) -> list[dict[str, str]]:
    text = DOC.read_text(encoding="utf-8")
    m = re.search(rf"<!-- {tag}:start -->\n(.*?)<!-- {tag}:end -->", text, re.S)
    assert m, tag
    lines = [ln for ln in m.group(1).strip().splitlines() if ln.startswith("|")]
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    return [dict(zip(head, [c.strip() for c in ln.strip("|").split("|")])) for ln in lines[2:]]


def _lf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def test_the_documents_tables_are_the_modules() -> None:
    parent = {r["file"]: r["LF sha256 (E-283)"].strip("`") for r in _table("wave42-r2-parent")}
    assert parent == R2.PARENT_SHA256
    for rel, want in parent.items():                       # W42-R1's pinned files, unedited
        assert _lf(ROOT / rel) == want, rel
    consts = {r["constant"]: json.loads(r["value"].strip("`")) for r in _table("wave42-r2-constants")}
    assert consts == R2.CONSTANTS_DELTA and R2.CONSTANTS == {**R.CONSTANTS, **consts}
    (lim,) = _table("wave42-r2-limits")
    L = R2.NET12_LIMIT
    assert (lim["name"], lim["measure"], lim["key"].strip("`"), lim["direction"], int(lim["horizon"]), lim["stat"],
            lim["optional"]) == (L.name, L.measure, L.key, L.direction, L.horizon, L.stat, "no") and not L.optional
    (req,) = _table("wave42-r2-required")
    assert (req["key"].strip("`"), int(req["horizon"]), float(req["low"]), float(req["high"])) == \
        ("net_month_12", *R2.REQUIRED["net_month_12"])
    text = DOC.read_text(encoding="utf-8")
    assert R2.PARENT_PIN_COMMIT in text and "E-283" in text


# ------------------------------------------------------------------------------------ the binding and the refusals
def test_the_readings_without_net_month_12_must_be_the_collections(pair) -> None:
    other = T._with(pair.rx, "p15", "orders_max", lambda x: x + 1.0)      # not the collection's readings
    with pytest.raises(R.Wave42Refused, match="readings_sha256"):
        _r2(other, pair.rs)


def test_the_held_out_guard_still_runs_first(pair) -> None:
    bad = T._retag(pair.rx, "p14", block="held_out")
    with pytest.raises(R.Wave42Refused, match="only the search years"):
        _r2(bad, pair.rs)


@pytest.mark.parametrize("how", ["missing", "blank", "infinite"])
def test_a_missing_blank_or_infinite_net_month_12_is_refused(pair, how) -> None:
    if how == "missing":
        rx = {b: R.BaselineReading(r.name, r.block, r.reading, r.starts, r.seeds,
                                   {k: v for k, v in r.values.items() if k != "net_month_12"} if b == "p16"
                                   else r.values) for b, r in pair.rx.items()}
        match = "lacks the required measure 'net_month_12'"
    else:
        val = np.nan if how == "blank" else np.inf
        rx = T._with(pair.rx, "p16", "net_month_12", lambda x: np.where(np.arange(x.shape[0])[:, None] == 0, val, x))
        match = "blank or not finite on E_252"
    with pytest.raises(R.Wave42Refused, match=match):
        _r2(rx, pair.rs)


@pytest.mark.parametrize("src", [{"p14": "d" * 64}, {**UNITS, "p14": "D" * 64}, {**UNITS, "p14": "d" * 63}, "d" * 64])
def test_the_source_names_the_four_units_files(pair, src) -> None:
    with pytest.raises(R.Wave42Refused, match="one units file sha256"):
        _r2(pair.rx, pair.rs, src=src)


def test_the_collection_route_needs_the_collections_digest_to_cover_the_column(pair) -> None:
    covered = T._bind(pair.rx)                             # a collection whose own digest covers net_month_12
    v = _r2(pair.rx, pair.rs, h4=covered, src=None).values
    assert v["r2"]["net12_source"].startswith("the collection")
    assert _net(v)["value"] == _net(pair.r2.values)["value"]
    with pytest.raises(R.Wave42Refused, match="readings_sha256"):
        _r2(pair.rx, pair.rs, src=None)                    # the collection's digest does not cover it


def test_the_floor_needs_net_month_12_and_off_needs_nothing_new(pair) -> None:
    with pytest.raises(R.Wave42Refused, match="lacks the required measure 'net_month_12'"):
        _r2(pair.rs, pair.rs)


# --------------------------------------------------------------------------- vacuity, the r2 block, the survey's path
def test_a_floor_below_zero_is_not_vacuous_for_net_cash() -> None:
    rs = T._readings()
    rx = _net12(rs, law=[(-6.0, 10.0), (-4.0, 10.0), (-3.0, 10.0), (-2.0, 10.0)])
    v = _r2(rx, rs).values
    net = _net(v)
    assert net["value"] < 0 and net["vacuous"] is False and net["vacuous_reason"] is None
    assert net["a_priori_range"] == ["-inf", "inf"]
    assert v["r2"]["floor_refuses_do_nothing"] is False and v["r2"]["inactivity"].startswith("not a guard")
    assert v["r2"]["null_journeys"]["do_nothing"] == {"net_month_12": 0.0, "inside": True}
    assert v["r2"]["null_journeys"]["quit_at_first_failure"]["net_month_12"] == -T.FEE


def test_a_floor_at_every_unit_is_vacuous() -> None:
    rs = T._readings()
    rx = _net12(rs)
    lowest = float(np.nanmin(np.concatenate([np.asarray(r.values["net_month_12"]).ravel() for r in rx.values()])))
    rx = T._with(rx, "naive_coin", "net_month_12", lambda x: np.where(np.isnan(x), np.nan, lowest - 1.0))
    net = _net(_r2(rx, rs).values)
    assert net["value"] == lowest - 1.0 and net["vacuous"] is True and net["vacuous_reason"].startswith("beyond every")


def test_a_positive_floor_refuses_the_do_nothing_journey(pair) -> None:
    r2b = pair.r2.values["r2"]
    assert r2b["value"] > 0 and r2b["floor_refuses_do_nothing"] is True and r2b["inactivity"].startswith("live")
    assert r2b["null_journeys"]["do_nothing"] == {"net_month_12": 0.0, "inside": False}
    assert r2b["null_journeys"]["quit_at_first_failure"] == {"net_month_12": -T.FEE, "inside": False}
    assert r2b["parent"]["sha256"] == R2.PARENT_SHA256 and r2b["limits_set"] == 7
    assert r2b["net12_source"] == {"units_files_sha256": UNITS}
    assert r2b["report_with_and_without_floor"].startswith("F-13's finalists are shown with and without")


def test_the_surveys_path_reads_the_added_limit_and_w42_r1s_cannot(pair) -> None:
    v, sl = pair.r2.values, T._sl()
    design = dict(pair.rx["p16"].values)
    value = _net(v)["value"]
    c = R2.limit_check(v, sl, design, R2.NET12_LIMIT.name, value)
    assert c["inside"] is True and c["estimate"] == pytest.approx(_net(v)["baseline_values"]["p16"], rel=1e-12)
    assert R2.limit_estimate(v, sl, design, R2.NET12_LIMIT.name) == c["estimate"]
    with pytest.raises(KeyError):
        R.limit_check(v, sl, design, R2.NET12_LIMIT.name, value)
    assert R2.pinned_inputs(v)["limits"][R2.NET12_LIMIT.name]["value"] == value
    assert R2.values_from_rows([{"key": k, "value_json": json.dumps(x)} for k, x in v.items()]) == \
        json.loads(json.dumps(v))


# ---------------------------------------------------------------------------------------------- the application
def _units_csv(path: Path, reading: R.BaselineReading, *, extra_rows: bool = True, tamper=None) -> None:
    keys = ("net_month_12", *sorted(R.REQUIRED))
    cols = list(AP.UNIT_ID_COLUMNS) + ["strict_overlaps"] + list(keys)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        mats = {k: np.asarray(reading.values[k], dtype=float) for k in keys}
        arms = [("off", R.READING)] + ([("stress_cost", R.READING), ("off", "as_walked")] if extra_rows else [])
        for arm, rdg in arms:
            for si, d in enumerate(reading.starts):
                for ci, c in enumerate(reading.seeds):
                    vals = ["" if math.isnan(mats[k][si, ci]) else repr(float(mats[k][si, ci]) + (arm != "off"))
                            for k in keys]
                    row = [reading.name, arm, rdg, "search", d, str(c), "0", *vals]
                    if tamper:
                        row = tamper(row, cols)
                    w.writerow(row)


def _sidecar(p: Path) -> str:
    sha = AP.A.sha256_file(p)
    Path(f"{p}.manifest.json").write_text(json.dumps({"sha256": sha}), encoding="utf-8")
    return sha


def _held_out_csv(n: int) -> bytes:
    d = np.arange(np.datetime64("2024-01-02"), np.datetime64("2026-12-31"))
    dates = [str(x) for x in d[np.is_busday(d)]][:n]
    return ("ordinal,date\n" + "".join(f"{i},{x}\n" for i, x in enumerate(dates))).encode("utf-8")


class Writer:
    def __init__(self):
        self.calls = []

    def __call__(self, df, name, **kw):
        out = Path(kw["results_dir"]) / name
        assert not out.exists()
        self.calls.append((name, kw))
        out.write_text(df.to_csv(index=False), encoding="utf-8")
        Path(f"{out}.manifest.json").write_text(json.dumps({"parameters": kw["parameters"]}, default=str),
                                                encoding="utf-8")
        return out, Path(f"{out}.manifest.json")


@pytest.fixture(scope="module")
def files(tmp_path_factory):
    """A synthetic results folder: H4's collection (its digest over W42-R1's keys) and four units files carrying
    `net_month_12` beside every W42-R1 measure, each with its sidecar; the held-out calendar."""
    d = tmp_path_factory.mktemp("w42r2") / "results"
    d.mkdir()
    rs = T._readings()
    rx = _net12(rs, law=[(2.0, 20.0), (4.0, 20.0), (6.0, 20.0), (8.0, 20.0)])
    shas = {}
    for b in R.BASELINES:
        p = d / f"h4_units_{b}.csv"
        _units_csv(p, rx[b])
        shas[b] = _sidecar(p)
    body = ("synthetic collection " + R.readings_digest(rs) + "\n").encode("utf-8")
    (d / R.COLLECTION_RESULT).write_bytes(body)
    params = {k: v for k, v in T._manifest(rs).items() if k != "sha256"}
    params["units_files_sha256"] = shas
    (d / f"{R.COLLECTION_RESULT}.manifest.json").write_text(
        json.dumps({"sha256": AP.A.sha256_bytes(body), "parameters": params}), encoding="utf-8")
    (d / R.HELD_OUT_CALENDAR).write_bytes(_held_out_csv(T.NHO))
    return SimpleNamespace(d=d, rs=rs, rx=rx, shas=shas)


@pytest.fixture()
def env(files, tmp_path, monkeypatch):
    d = tmp_path / "results"
    shutil.copytree(files.d, d)
    monkeypatch.setattr(R, "HELD_OUT_CALENDAR_SHA256", AP.A.sha256_file(d / R.HELD_OUT_CALENDAR))
    monkeypatch.setattr(R, "SEARCH_CALENDAR_SHA256", "c" * 64)
    w = Writer()
    src = AP.A.Sources(adapter=lambda path, man: files.rs,
                       calendar_loader=lambda path: SimpleNamespace(dates=T.CAL, calendar_sha256=R.calendar_digest(T.CAL),
                                                                    file_sha256="c" * 64),
                       fee=lambda: (T.FEE, R.FEE_SOURCE, "f" * 64), writer=w)
    return SimpleNamespace(d=d, src=src, w=w, f=files)


def test_the_application_applies_once_reading_net_month_12_from_the_units_files(env) -> None:
    params = AP.apply(env.d, env.src)
    assert [c[0] for c in env.w.calls] == [R2.OUTPUT_NAME] and (env.d / R2.OUTPUT_NAME).is_file()
    assert params["rule_id"] == "W42-R2" and params["parent_rule_id"] == "W42-R1"
    assert params["units_files_sha256"] == env.f.shas
    assert params["readings_sha256"] == R.readings_digest(env.f.rs)
    assert params["r2_readings_sha256"] == R.readings_digest(env.f.rx)
    assert params["parent_sha256"] == R2.PARENT_SHA256
    direct = R2.setting_rule(env.f.rx, h4=R.H4Binding(params["h4_result_sha256"], T._manifest(
        env.f.rs, sha256=params["h4_result_sha256"])), search_calendar=T.CAL, fee_unit=T.FEE,
        fee_source=R.FEE_SOURCE, test_starts=T.TEST_STARTS,
        test_starts_source={"file": R.HELD_OUT_CALENDAR, "sha256": R.HELD_OUT_CALENDAR_SHA256, "sessions": T.NHO},
        net12_source=env.f.shas)
    assert params["values_sha256"] == direct.digest()
    with pytest.raises(AP.ApplyRefused, match="applied once"):
        AP.apply(env.d, env.src)
    assert len(env.w.calls) == 1


def test_a_w42_r1_output_refuses_the_application(env) -> None:
    (env.d / R.OUTPUT_NAME).write_text("key,value_json\n", encoding="utf-8")
    with pytest.raises(AP.ApplyRefused, match="applied once"):
        AP.apply(env.d, env.src)
    assert env.w.calls == []


def test_a_units_file_that_is_not_the_one_the_collection_read_is_refused(env) -> None:
    p = env.d / "h4_units_p15.csv"
    _units_csv(p, env.f.rx["p15"], extra_rows=False)       # another file: its sha256 is not the collection's record
    _sidecar(p)
    with pytest.raises(AP.ApplyRefused, match="not the units file H4's collection read"):
        AP.apply(env.d, env.src)
    assert env.w.calls == []


def test_a_units_file_not_its_sidecars_is_refused(env) -> None:
    p = env.d / "h4_units_p14.csv"
    p.write_bytes(p.read_bytes() + b"\n")
    with pytest.raises(AP.ApplyRefused, match="not its sidecar's"):
        AP.apply(env.d, env.src)


def _rewrite(env, b: str, tamper) -> None:
    """A units file rewritten with `tamper`, its sidecar and the collection's record made to match, so that only the
    loader's own check can refuse it."""
    p = env.d / f"h4_units_{b}.csv"
    _units_csv(p, env.f.rx[b], tamper=tamper)
    sha = _sidecar(p)
    side = env.d / f"{R.COLLECTION_RESULT}.manifest.json"
    man = json.loads(side.read_text(encoding="utf-8"))
    man["parameters"]["units_files_sha256"][b] = sha
    side.write_text(json.dumps(man), encoding="utf-8")


def test_a_held_out_row_is_refused_before_anything_else(env) -> None:
    first = {"done": False}

    def tamper(row, cols):
        if not first["done"]:
            first["done"] = True
            row[cols.index("block")] = "held_out"
            row[cols.index("arm")] = "stress_cost"
        return row
    _rewrite(env, "p16", tamper)
    with pytest.raises(AP.ApplyRefused, match="only the search years are read"):
        AP.apply(env.d, env.src)


def test_a_measure_differing_from_the_collections_is_refused(env) -> None:
    def tamper(row, cols):
        if row[cols.index("arm")] == "off" and row[cols.index("reading")] == R.READING \
                and row[cols.index("seed")] == "1" and row[cols.index("orders_max")] != "":
            row[cols.index("orders_max")] = repr(float(row[cols.index("orders_max")]) + 1.0)
        return row
    _rewrite(env, "naive_coin", tamper)
    with pytest.raises(AP.ApplyRefused, match="orders_max is not the collection's"):
        AP.apply(env.d, env.src)


def test_a_missing_units_record_or_file_is_refused(env) -> None:
    (env.d / "h4_units_p14.csv").unlink()
    with pytest.raises(AP.ApplyRefused, match="units file h4_units_p14.csv and its sidecar"):
        AP.apply(env.d, env.src)
    side = env.d / f"{R.COLLECTION_RESULT}.manifest.json"
    man = json.loads(side.read_text(encoding="utf-8"))
    del man["parameters"]["units_files_sha256"]
    side.write_text(json.dumps(man), encoding="utf-8")
    with pytest.raises(AP.ApplyRefused, match="records no units_files_sha256"):
        AP.apply(env.d, env.src)


def test_the_freeze_reads_w42_r2s_pin_file_and_files_and_refuses_until_pinned() -> None:
    fn = AP._r2_functions()
    assert fn["PIN_FILE"] == "config/w42_r2_pin.json"
    assert fn["commit_problem"].__code__ is AP.A.commit_problem.__code__
    assert set(AP.A.IMPORTED_FILES) < set(AP.IMPORTED_FILES)
    assert {"extended/wave42_r2.py", "scripts/wave42_r2_apply.py", "docs/plans/WAVE42_SETTING_RULE_R2.md"} <= \
        set(AP.IMPORTED_FILES)
    assert AP.A.PIN_FILE == "config/w42_r1_pin.json" and AP.A.IMPORTED_FILES == tuple(AP.A.IMPORTED_FILES)
    if not (ROOT / "config" / "w42_r2_pin.json").is_file():
        assert AP.pinned_commit(ROOT) is None
        assert "config/w42_r2_pin.json" in AP.commit_problem(ROOT, None)


# ---------------------------------------------------------------------------------------------- the power check
def test_the_power_check_at_a_reduced_count() -> None:
    """The machinery of every part at a reduced count (the full check's figures are `tests/w42r2_power.py`'s)."""
    r = PW.run_size("rt_unequal_sd", reps=40)
    assert r["reps"] == 40 and r["j_h4"] == HA.H4_J and r["j_test"] == R.TEST_SEEDS and r["tolerance"] == 1.4
    assert set(r["refusal"]) == set(PW.FORMS) and r["c1_bound"] == PW.c1_bound(1.4, n=40)
    assert r["share_headroom_bound"]["sd_star"] >= r["share_headroom_bound"]["winner"]
    assert PW.run_size("lattice", reps=10)["c6_exception"] is True
    c = PW.run_configs(4, 500)
    assert set(c["max_ratio"]) == set(PW.FORMS) and c["configs"] == 4
    j = PW.aggregate_joint([PW.run_joint(0, 1, 1)])
    assert j["search_draws"] == 1 and set(j["limits"]) == {L.name for L in R2.LIMITS}
    e = PW.run_e2e("identical", 1, 1)
    assert e["share_headroom_bound"] == 1.0 and e["c4_pass"] and "c1_pass" in e
    d = PW.run_e2e("behind", 1, 1)
    assert d["c6_exception_forms_identical"] and d["c4_pass"] and d["floor_mean"]["sd_star"] < 0


def test_the_power_checks_seed_is_derived_from_its_name() -> None:
    assert PW.ROOT_ENTROPY == int.from_bytes(hashlib.sha256(PW.CHECK_NAME.encode("utf-8")).digest()[:16], "big")
    law = PW.Law("two_humped", (0.55, 12.0, 4.0, -4.0, 1.5))
    m = law.median(1.0)
    x = law.draw(np.random.default_rng(np.random.SeedSequence(PW.ROOT_ENTROPY, spawn_key=(99,))), (400000,), 1.0)
    assert abs(float(np.median(x)) - m) < 5 * law.median_se(1.0, x.size)


def test_the_lattice_exception_holds_only_inside_the_lattice_step() -> None:
    """R-2: C6's lattice exception is checked in code: every form's headroom, in every replication, is narrower than
    the smallest lattice step; a scenario whose step is narrower than the headroom loses the exception."""
    r = PW.run_size("lattice", reps=30)
    assert r["lattice_step"] == 1.0 and 0.0 < r["widest_headroom"] < r["lattice_step"] and r["c6_exception"] is True
    assert PW.lattice_step(PW.Law("lattice", ((2.0, 3.0, 4.0), (0.5, 0.4, 0.1)))) == 1.0
    fine = dict(PW.SIZE["lattice"])
    fine["laws"] = [PW.Law("lattice", ((2.0, 3.0, 3.0001, 4.0), (0.5, 0.2, 0.2, 0.1)))] * 4
    PW.SIZE["lattice_fine_r2"] = fine
    try:
        f = PW.run_size("lattice_fine_r2", reps=5)
    finally:
        del PW.SIZE["lattice_fine_r2"]
    assert f["lattice_step"] == pytest.approx(0.0001) and f["c6_exception"] is False
    for name in ("rt_unequal_sd", "equal_independent"):
        assert PW.run_size(name, reps=5)["c6_exception"] is False
