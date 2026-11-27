"""W42-R2 (`docs/plans/WAVE42_SETTING_RULE_R2.md`, `extended/wave42_r2.py`, `scripts/wave42_r2_apply.py`): W42-R1 with
one added limit, a floor on the median 12-month net cash. Synthetic readings only (W42-R1's tests' generator), no bar,
no result file of this repository, no held-out outcome:

- **W42-R1 unchanged with the limit off**: the same output, digest for digest; W42-R1's module untouched; W42-R1's own
  code objects run;
- **only the stated keys move with it on**, and W42-R1's six limits move only through z at L = 7 where the headroom
  binds;
- **the floor's value comes from W42-R1's formula** (recomputed here by the text's words), moves with the baselines,
  and no number is typed in its definition;
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
MOVING = {"rule_id", "constants", "application", "limits", "h4", "input_sha256", "r2"}


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
    la = {x["name"]: x for x in a["limits"]["values"]}
    lb = {x["name"]: x for x in b["limits"]["values"]}
    assert list(lb) == [L.name for L in R.LIMITS] + [R2.NET12_LIMIT.name]
    for name, x in la.items():
        y = lb[name]
        for k in ("baseline_values", "best", "worst", "best_se_test", "by_search_year", "direction", "stat"):
            assert x[k] == y[k], (name, k)
        assert y["headroom_z"] == b["limits"]["headroom_z"]
        if y["binds"] == "worst_baseline":
            assert y["value"] == y["baseline_values"][y["worst"]]
        else:
            sign = 1.0 if y["direction"] == "ceiling" else -1.0
            assert y["value"] == pytest.approx(y["baseline_values"][y["best"]] + sign * y["headroom_z"]
                                               * y["best_se_test"], rel=1e-12)


def test_a_headroom_bound_w42_r1_limit_moves_out_by_z_at_seven_and_nothing_else_does() -> None:
    rs = T._readings()
    same = np.asarray(rs["p14"].values["taken_mean"], dtype=float)
    for b in R.BASELINES:                                  # every baseline equal on taken_mean: the headroom binds
        rs = T._with(rs, b, "taken_mean", lambda _x: same.copy())
    rx = _net12(rs)
    a, b = T._run(rs).values, _r2(rx, rs).values
    x = next(v for v in a["limits"]["values"] if v["name"] == "taken_mean_p10")
    y = next(v for v in b["limits"]["values"] if v["name"] == "taken_mean_p10")
    assert x["binds"] == y["binds"] == "headroom"
    assert x["value"] == pytest.approx(x["baseline_values"][x["best"]] - R.limit_z(6) * x["best_se_test"], rel=1e-12)
    assert y["value"] == pytest.approx(y["baseline_values"][y["best"]] - R.limit_z(7) * y["best_se_test"], rel=1e-12)
    assert y["value"] < x["value"]                         # a floor: further out is lower


# ------------------------------------------------------------------------------- the value comes from the formula
def _formula(rx, J=R.TEST_SEEDS):
    """Section 3.2 by its words, independently of the module: the median of the pooled units of E_252, the per-seed
    standard deviation of the best's, the test standard error, z at L = 7, the floor."""
    sl = T._sl(rx[R.BASELINES[0]].starts)
    e = sl >= 252
    X = {b: np.asarray(rx[b].values["net_month_12"], dtype=float)[e] for b in R.BASELINES}
    M = {b: float(np.quantile(X[b].ravel(), 0.5)) for b in R.BASELINES}
    best = max(R.BASELINES, key=lambda b: (M[b], -R.BASELINES.index(b)))
    worst = min(R.BASELINES, key=lambda b: (M[b], R.BASELINES.index(b)))
    sd = float(np.std([np.quantile(X[best][:, c], 0.5) for c in range(X[best].shape[1])], ddof=1))
    se = sd * math.sqrt(int(e.sum()) / (J * T.TEST_STARTS[252]))
    z = float(stats.norm.ppf(1.0 - (1.0 - 0.8) / 7))
    need = M[best] - z * se
    return {"M": M, "best": best, "worst": worst, "se": se, "value": min(M[worst], need),
            "binds": "worst_baseline" if M[worst] <= need else "headroom"}


def test_the_floors_value_is_w42_r1s_formula_recomputed_from_the_readings(pair) -> None:
    f, net = _formula(pair.rx), _net(pair.r2.values)
    assert net["value"] == pytest.approx(f["value"], rel=1e-12)
    assert net["binds"] == f["binds"] and net["best"] == f["best"] and net["worst"] == f["worst"]
    assert net["best_se_test"] == pytest.approx(f["se"], rel=1e-12)
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
    """The full check's figures are `python tests/w42r2_power.py`'s; here, two search draws by two held-out draws."""
    d = PW.run_scenario("distinct", search_draws=2, held_out_draws=2)
    assert d["limits_set"] == 7 and d["test_seeds"] == R.TEST_SEEDS and d["h4_seeds"] == 128
    assert d["power_margin"] == 1.0 and d["do_nothing_refused"] == 1.0
    assert d["false_refusal"]["equal_to_best"] == 0.0 and d["floor_mean"] > 0
    assert d["pass_rate"]["curve_t-2"] <= d["pass_rate"]["curve_t+6"] == 1.0
    i = PW.run_scenario("identical", search_draws=2, held_out_draws=2)
    assert i["share_binds_headroom"] == 1.0 and i["power_margin"] == 1.0
    b = PW.run_scenario("behind", search_draws=1, held_out_draws=2)
    assert b["floor_mean"] < 0 and b["do_nothing_refused"] == 0.0 and b["power_margin"] == 1.0


def test_the_power_checks_seed_is_derived_from_its_name() -> None:
    assert PW.ROOT_ENTROPY == int.from_bytes(hashlib.sha256(PW.CHECK_NAME.encode("utf-8")).digest()[:16], "big")
    law = PW.Law("two_humped", (0.55, 12.0, 4.0, -4.0, 1.5))
    m = law.median(1.0)
    x = law.draw(np.random.default_rng(np.random.SeedSequence(PW.ROOT_ENTROPY, spawn_key=(99,))), (400000,), 1.0)
    assert abs(float(np.median(x)) - m) < 5 * law.median_se(1.0, x.size)
