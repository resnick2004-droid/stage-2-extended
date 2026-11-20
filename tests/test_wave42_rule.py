"""Wave 4.2's setting rule (`docs/plans/WAVE42_SETTING_RULE.md`, `extended/wave42.py`), on synthetic baseline readings
only (no engine, no bar, no result file; fast):

- **deterministic** -- the same input twice, the readings as a list or a reordered mapping, give the same JSON and digest;
- **traced** -- each output equals its stated input recomputed here by the text's formula (the budgets from the pooled
  quantile and the fee lattice, the caps, the ROC weights, delta\\* from the resolved gaps, each limit from the worst
  baseline or the headroom, the power from 2.5's formula), and the input's digest moves with any input;
- **refusing** -- a held-out tag, a held-out or confirmation-window start day, a missing baseline, unpaired seeds, a
  blank inside E_h, an out-of-range value: refused before any value is computed;
- **moving as the text says** -- section 7's table, one test per row;
- **the document's constants are the module's**, machine-read from its tables, and the search years are E-208's.
"""
from __future__ import annotations

import ast
import copy
import json
import math
import re
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from extended import wave42 as R

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "plans" / "WAVE42_SETTING_RULE.md"
FEE = 50.0                                   # a synthetic fee unit (the real one is read from the verified ledger)
SRC = "synthetic test fee"
N, J0 = 360, 6
TEST_STARTS = {63: 580, 126: 520, 252: 390}  # synthetic counts (the real ones are the three-way test's arithmetic)


def _dates(n: int) -> tuple[str, ...]:
    d = np.busday_offset("2020-01-02", np.arange(n), roll="forward")
    return tuple(str(x) for x in d)


def _reading(name: str, seed: int, *, pay: float, spend: float, n: int = N, J: int = J0) -> R.BaselineReading:
    """One synthetic baseline: `pay` moves the payout odds and the months ahead, `spend` the fee multiples."""
    rng = np.random.default_rng(seed)
    sl = np.arange(n, 0, -1) + 20                                 # strictly decreasing; E_252 is the first n - 232 + 20
    paid = rng.random((n, J)) < pay
    days = np.where(paid, rng.integers(10, R.W + 1, (n, J)), R.W + 1).astype(float)
    k6 = rng.integers(1, int(2 + 8 * spend), (n, J))
    x6 = k6 * FEE
    x2 = np.minimum(x6, rng.integers(1, 4, (n, J)) * FEE).astype(float)
    v = {"spent_before_first_payout": x6.astype(float), "first_payout_days": days, "cash_to_first_pass": x2}
    for m in (1, 2, 3):
        v[f"net_month_{m}"] = rng.normal(400 * (pay - 0.5), 900, (n, J))
        v[f"peak_month_{m}"] = np.minimum(x6, FEE * m * (1 + spend)) + 0.0
    v["peak_oop_12_months"] = x6 + rng.integers(0, 4, (n, J)) * FEE
    v["share_months_positive"] = rng.integers(0, 13, (n, J)) / 12.0
    v["orders_max"] = rng.integers(1, 6, (n, J)).astype(float)
    v["accounts_max"] = rng.integers(1, 4, (n, J)).astype(float)
    v["taken_mean"] = rng.random((n, J)) * 3
    for key, (h, _, _) in {**R.REQUIRED, **R.OPTIONAL}.items():  # blanks outside E_h are allowed (the blank rule)
        v[key] = v[key].copy()
        v[key][sl < h] = np.nan
    return R.BaselineReading(name, "search", _dates(n), tuple(int(x) for x in sl), tuple(range(1, J + 1)), v)


def _readings(**over) -> dict[str, R.BaselineReading]:
    p = {"naive_coin": (11, 0.35, 0.9), "p14": (12, 0.6, 0.4), "p15": (13, 0.55, 0.5), "p16": (14, 0.7, 0.3)}
    p.update(over)
    return {b: _reading(b, s, pay=a, spend=c) for b, (s, a, c) in p.items()}


def _run(rs, J: int = 200, starts=None) -> R.Wave42Values:
    return R.setting_rule(rs, fee_unit=FEE, fee_source=SRC, test_starts=starts or TEST_STARTS, test_seeds=J)


def _with(rs, name, key, fn):
    """A copy of the readings with one baseline's measure replaced by fn(old)."""
    rs = dict(rs)
    b = rs[name]
    vals = dict(b.values)
    vals[key] = fn(np.asarray(vals[key], dtype=float).copy())
    rs[name] = R.BaselineReading(b.name, b.block, b.starts, b.sessions_left, b.seeds, vals)
    return rs


@pytest.fixture(scope="module")
def base():
    rs = _readings()
    return rs, _run(rs)


# ------------------------------------------------------------------------------------------------ deterministic
def test_deterministic_and_order_free(base) -> None:
    rs, v = base
    again = _run(copy.deepcopy(rs))
    assert again.as_json() == v.as_json() and again.digest() == v.digest()
    rev = {k: rs[k] for k in reversed(list(rs))}
    assert _run(rev).digest() == v.digest()
    assert _run(list(rs.values())).digest() == v.digest()
    json.loads(v.as_json())                                         # finite, canonical JSON


# ------------------------------------------------------------------------------------------------------ traced
def _pooled(rs, key, h):
    sl = np.asarray(rs["p14"].sessions_left)
    return np.concatenate([np.asarray(rs[b].values[key])[sl >= h].ravel() for b in R.BASELINES])


def test_budgets_trace_to_the_pooled_spending_and_the_fee_lattice(base) -> None:
    rs, v = base
    b = v.values["budgets"]
    x = _pooled(rs, "spent_before_first_payout", R.W)
    for t, p in zip(b["trace"], R.BUDGET_QUANTILES):
        assert t["pooled_value"] == pytest.approx(np.quantile(x, p))
        assert t["budget"] == FEE * max(1, math.ceil(np.quantile(x, p) / FEE - 1e-9))
        assert t["budget"] >= t["pooled_value"] and t["budget"] - t["pooled_value"] < FEE
    assert b["primary"] == R.fee_lattice(float(np.quantile(x, R.PRIMARY_BUDGET_QUANTILE)), FEE)
    assert b["fee_source"] == SRC and b["units_pooled"] == x.size
    assert b["values"] == sorted(set(b["values"]))


def test_caps_weights_and_composite_trace(base) -> None:
    rs, v = base
    dims = {d["name"]: d for d in v.values["dimensions"]}
    x = _pooled(rs, "peak_oop_12_months", 252)
    ql, qh = np.quantile(x, R.CAP_QUANTILES)
    assert dims["bankroll"]["lo"] == pytest.approx(max(0.0, ql - R.CAP_MARGIN * (qh - ql)))
    assert dims["bankroll"]["hi"] == pytest.approx(qh + R.CAP_MARGIN * (qh - ql))
    assert (dims["money"]["lo"], dims["money"]["hi"]) == (0.0, 1.0)
    kept = [d["name"] for d in v.values["dimensions"] if d["kept"]]
    assert kept[0] == "money"
    assert list(v.values["weights"].values()) == pytest.approx(R.roc_weights(len(kept)))
    assert sum(v.values["weights"].values()) == pytest.approx(1.0)
    C = v.values["composite"]["value"]
    for b in R.BASELINES:     # the composite is the weighted sum of the dimensions' baseline means
        assert C[b] == pytest.approx(sum(v.values["weights"][k] * dims[k]["baseline_means"][b] for k in kept))
    assert v.values["composite"]["ranking"] == sorted(R.BASELINES, key=lambda b: (-C[b], R.BASELINES.index(b)))


def test_roc_weights_known_values() -> None:
    assert R.roc_weights(1) == [1.0]
    assert R.roc_weights(2) == pytest.approx([0.75, 0.25])
    assert R.roc_weights(3) == pytest.approx([11 / 18, 5 / 18, 2 / 18])


def test_delta_star_and_power_trace(base) -> None:
    _, v = base
    d, p = v.values["delta_star"], v.values["power"]
    res = [g["gap"] for g in d["gaps"] if g["resolved"]]
    raw = min(res) if res else R.DELTA_FRACTION * d["spread"]
    assert d["raw"] == pytest.approx(raw) and d["value"] == max(R.DELTA_MIN, raw)
    for g in d["gaps"]:
        assert g["resolved"] == (g["gap"] > R.RESOLVE_Z * g["se"])
    assert p["alpha"] == pytest.approx(0.05 / (13 * 14))
    best = v.values["composite"]["ranking"][0]
    assert p["pair_delta"][best] == pytest.approx(d["value"])
    lower = max(0.0, 1 - sum(1 - x for x in p["pair_power"].values()))
    assert p["conjoint_lower"] == pytest.approx(lower)
    if p["J_needed"] is not None:
        w = v.values["weights"]
        hz = {x.name: x.horizon for x in R.DIMENSIONS}
        f = lambda J: R.conjoint_power(p["pair_delta"], p["pair_sigma"],   # noqa: E731
                                       R.q_factor(w, {k: hz[k] for k in w}, TEST_STARTS, J), p["alpha"])
        assert f(p["J_needed"]) >= R.POWER_TARGET
        assert p["J_needed"] == 1 or f(p["J_needed"] - 1) < R.POWER_TARGET


def test_power_formula_is_the_three_way_notes_on_one_horizon() -> None:
    alpha, n, J, delta, sig = R.level(13), 500, 40, 0.02, 0.6
    Q = R.q_factor({"a": 0.5, "b": 0.5}, {"a": 63, "b": 63}, {63: n}, J)
    assert Q == pytest.approx(1 / (J * n))
    ch = math.sqrt(2 * math.log(1 / alpha))
    assert R.pair_power(delta, Q, sig, alpha) == pytest.approx(stats.norm.cdf((math.sqrt(J * n) * delta - ch) / sig))
    assert R.pair_power(delta, Q, 0.0, alpha) in (0.0, 1.0)


def test_limits_trace_to_the_worst_baseline_or_the_headroom(base) -> None:
    rs, v = base
    sl = np.asarray(rs["p14"].sessions_left)
    lims = {x["name"]: x for x in v.values["limits"]["values"]}
    L = lims["first_payout_days_p50"]
    M = {b: float(np.quantile(np.asarray(rs[b].values["first_payout_days"])[sl >= R.W], 0.5)) for b in R.BASELINES}
    assert L["baseline_values"] == pytest.approx(M)
    worst = max(M.values())
    assert L["value"] == pytest.approx(max(worst, L["headroom_needed"]))
    assert L["binds"] == ("worst_baseline" if worst >= L["headroom_needed"] else "headroom")
    z = stats.norm.ppf(R.POWER_TARGET)
    assert L["headroom_needed"] == pytest.approx(min(M.values()) + z * L["best_se_test"])
    assert lims["not_paid_within_B"]["budget"] == v.values["budgets"]["primary"]
    assert lims["taken_mean_p10"]["direction"] == "floor"
    assert lims["taken_mean_p10"]["value"] <= min(lims["taken_mean_p10"]["baseline_values"].values()) + 1e-12
    assert v.values["limits"]["check_level"] == R.LIMIT_CHECK_LEVEL


def test_input_digest_moves_with_any_input(base) -> None:
    rs, v = base
    d0 = v.values["input_sha256"]
    assert _run(_with(rs, "p15", "net_month_2", lambda x: x + 1e-3)).values["input_sha256"] != d0
    assert R.setting_rule(rs, fee_unit=FEE, fee_source=SRC, test_starts=TEST_STARTS,
                          test_seeds=201).values["input_sha256"] != d0
    assert R.setting_rule(rs, fee_unit=FEE + 1, fee_source=SRC, test_starts=TEST_STARTS,
                          test_seeds=200).values["input_sha256"] != d0


# --------------------------------------------------------------------------------------------------- refusing
def _retag(rs, name, **kw):
    rs = dict(rs)
    b = rs[name]
    f = {"block": b.block, "starts": b.starts, "sessions_left": b.sessions_left, "seeds": b.seeds}
    f.update(kw)
    rs[name] = R.BaselineReading(b.name, f["block"], f["starts"], f["sessions_left"], f["seeds"], b.values)
    return rs


@pytest.mark.parametrize("tag", ["held_out", "heldout", "held-out", "confirmation", "Search", ""])
def test_refuses_a_held_out_tag(base, tag) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="block"):
        _run(_retag(rs, "p16", block=tag))


@pytest.mark.parametrize("day", ["2024-01-02", "2025-06-02", "2026-07-17", "2019-12-31"])
def test_refuses_a_start_day_outside_the_search_years(base, day) -> None:
    rs, _ = base
    starts = list(rs["p14"].starts)
    starts[-1] = day
    with pytest.raises(R.Wave42Refused, match="search years"):
        _run(_retag(rs, "p14", starts=tuple(starts)))


def test_refuses_malformed_input(base) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="exactly"):
        _run({k: rs[k] for k in ("naive_coin", "p14", "p15")})
    with pytest.raises(R.Wave42Refused, match="paired"):
        _run(_retag(rs, "p15", seeds=tuple(s + 100 for s in rs["p15"].seeds)))
    with pytest.raises(R.Wave42Refused, match="blank"):
        _run(_with(rs, "p14", "first_payout_days", lambda x: np.where(np.arange(N)[:, None] == 0, np.nan, x)))
    with pytest.raises(R.Wave42Refused, match="a priori"):
        _run(_with(rs, "p14", "share_months_positive", lambda x: x + 2.0))
    with pytest.raises(R.Wave42Refused, match="required"):
        b = rs["p16"]
        _run({**rs, "p16": R.BaselineReading(b.name, b.block, b.starts, b.sessions_left, b.seeds,
                                             {k: x for k, x in b.values.items() if k != "cash_to_first_pass"})})
    with pytest.raises(R.Wave42Refused, match="some baselines"):
        b = rs["p16"]
        _run({**rs, "p16": R.BaselineReading(b.name, b.block, b.starts, b.sessions_left, b.seeds,
                                             {k: x for k, x in b.values.items() if k != "orders_max"})})
    with pytest.raises(R.Wave42Refused, match="every horizon"):
        _run(rs, starts={63: 500, 126: 400})
    with pytest.raises(R.Wave42Refused, match="fee unit"):
        R.setting_rule(rs, fee_unit=0.0, fee_source=SRC, test_starts=TEST_STARTS, test_seeds=10)


# --------------------------------------------------------------------------------------- moving as the text says
def test_more_spending_raises_the_budgets(base) -> None:
    rs, v = base
    up = _run(_with(rs, "naive_coin", "spent_before_first_payout", lambda x: x + 3 * FEE))
    for a, b in zip(v.values["budgets"]["trace"], up.values["budgets"]["trace"]):
        assert b["budget"] >= a["budget"] and b["budget"] % FEE == 0
    assert up.values["budgets"]["primary"] >= v.values["budgets"]["primary"]


def test_a_worse_worst_baseline_moves_its_ceiling_and_a_better_best_does_not(base) -> None:
    rs, v = base
    name, key = "peak_oop_12_months_p90", "peak_oop_12_months"
    L0 = {x["name"]: x for x in v.values["limits"]["values"]}[name]
    assert L0["binds"] == "worst_baseline"
    worse = _run(_with(rs, L0["worst"], key, lambda x: x + 5 * FEE))
    L1 = {x["name"]: x for x in worse.values["limits"]["values"]}[name]
    assert L1["value"] == pytest.approx(L0["value"] + 5 * FEE)
    assert L1["value"] == pytest.approx(L1["baseline_values"][L0["worst"]])
    better = _run(_with(rs, L0["best"], key, lambda x: np.maximum(x - FEE, 0)))
    L2 = {x["name"]: x for x in better.values["limits"]["values"]}[name]
    assert L2["value"] == pytest.approx(L0["value"]) and L2["baseline_values"][L0["best"]] < L0["baseline_values"][L0["best"]]


def test_equal_baselines_set_the_limit_at_the_headroom(base) -> None:
    """Every baseline equal on supply (a floor): the worst is the best, so the headroom binds, below it by z_pi se."""
    rs, _ = base
    same = dict(rs)
    for b in R.BASELINES:
        same = _with(same, b, "taken_mean", lambda x: np.asarray(rs["p14"].values["taken_mean"], dtype=float))
    L = {x["name"]: x for x in _run(same).values["limits"]["values"]}["taken_mean_p10"]
    M = L["baseline_values"]["p14"]
    assert L["best_se_test"] > 0 and L["binds"] == "headroom" and L["value"] < M
    assert L["value"] == pytest.approx(M - stats.norm.ppf(R.POWER_TARGET) * L["best_se_test"])


def test_an_absent_optional_measure_sets_no_limit(base) -> None:
    rs, _ = base
    gone = {}
    for k, b in rs.items():
        gone[k] = R.BaselineReading(b.name, b.block, b.starts, b.sessions_left, b.seeds,
                                    {x: y for x, y in b.values.items() if x != "accounts_max"})
    L = {x["name"]: x for x in _run(gone).values["limits"]["values"]}["accounts_max_p90"]
    assert L["status"] == "not set"


def test_a_shifted_dollar_dimension_shifts_its_caps_and_nothing_else(base) -> None:
    rs, _ = base
    c = 10_000.0

    def shifted(t):
        out = dict(rs)
        for b in R.BASELINES:
            out = _with(out, b, "peak_oop_12_months", lambda x: x + t)
        return _run(out)

    s1, s2 = shifted(c), shifted(2 * c)                      # both far from the a priori floor of zero
    d1 = {d["name"]: d for d in s1.values["dimensions"]}["bankroll"]
    d2 = {d["name"]: d for d in s2.values["dimensions"]}["bankroll"]
    assert d1["lo"] > 0
    assert d2["lo"] == pytest.approx(d1["lo"] + c) and d2["hi"] == pytest.approx(d1["hi"] + c)
    assert s2.values["weights"] == s1.values["weights"]
    assert s2.values["composite"]["value"] == pytest.approx(s1.values["composite"]["value"])
    assert s2.values["delta_star"]["value"] == pytest.approx(s1.values["delta_star"]["value"])


def test_a_redundant_dimension_is_dropped_and_the_weights_reset(base) -> None:
    rs, _ = base
    red = dict(rs)
    for b in R.BASELINES:     # cost made a monotone function of speed: Spearman's rho is 1
        days = np.asarray(rs[b].values["first_payout_days"], dtype=float)
        red = _with(red, b, "cash_to_first_pass", lambda x, d=days: np.where(np.isnan(x), np.nan, 10.0 * d))
    v = _run(red)
    dims = {d["name"]: d for d in v.values["dimensions"]}
    assert not dims["cost"]["kept"] and dims["cost"]["reason"] == "redundant with speed"
    assert dims["cost"]["rho"] >= R.REDUNDANT_RHO and dims["cost"]["weight"] == 0.0
    kept = [d["name"] for d in v.values["dimensions"] if d["kept"]]
    assert list(v.values["weights"]) == kept
    assert list(v.values["weights"].values()) == pytest.approx(R.roc_weights(len(kept)))


def _aligned(seed: int, share_good: float) -> R.BaselineReading:
    """Every dimension a function of one binary level per unit: all redundant with money."""
    rng = np.random.default_rng(seed)
    sl = np.arange(N, 0, -1) + 20
    good = rng.random((N, J0)) < share_good
    g = good.astype(float)
    v = {"spent_before_first_payout": np.where(good, FEE, 4 * FEE), "first_payout_days": np.where(good, 20.0, R.W + 1.0),
         "cash_to_first_pass": np.where(good, FEE, 3 * FEE), "peak_oop_12_months": np.where(good, FEE, 4 * FEE),
         "share_months_positive": g}
    for m in (1, 2, 3):
        v[f"net_month_{m}"] = np.where(good, 100.0, -100.0)
        v[f"peak_month_{m}"] = np.where(good, FEE, 4 * FEE)
    return R.BaselineReading("x", "search", _dates(N), tuple(int(x) for x in sl), tuple(range(1, J0 + 1)), v)


def test_all_redundant_gives_the_fallback() -> None:
    rs = {}
    for i, b in enumerate(R.BASELINES):
        r = _aligned(21 + i, 0.72 + 0.02 * i)
        rs[b] = R.BaselineReading(b, r.block, r.starts, r.sessions_left, r.seeds, r.values)
    v = _run(rs)
    assert v.values["budgets"]["primary"] == FEE
    assert v.values["form"] == "fallback" and v.values["weights"] == {"money": 1.0}
    assert all(not d["kept"] for d in v.values["dimensions"][1:])
    assert {x["name"]: x for x in v.values["limits"]["values"]}["orders_max_p90"]["status"] == "not set"


def test_identical_baselines_put_delta_star_at_its_floor(base) -> None:
    rs, _ = base
    same = {b: R.BaselineReading(b, rs["p14"].block, rs["p14"].starts, rs["p14"].sessions_left, rs["p14"].seeds,
                                 rs["p14"].values) for b in R.BASELINES}
    v = _run(same)
    d = v.values["delta_star"]
    assert all(not g["resolved"] and g["gap"] == 0 for g in d["gaps"])
    assert d["spread"] == 0 and d["value"] == R.DELTA_MIN and "floor" in d["how"]
    assert v.values["composite"]["ranking"] == list(R.BASELINES)          # ties broken in the declared order


def test_unresolved_gaps_use_the_fraction_of_the_spread() -> None:
    """Four identical baselines on two seeds, P-16 better on seed 1 only: its gap is (a, 0) per seed, so its mean a / 2
    is below RESOLVE_Z x its standard error a / 2 -- no gap is resolved, and delta* is the fraction of the spread."""
    r = _reading("p14", 12, pay=0.5, spend=0.5, J=2)
    same = {b: R.BaselineReading(b, r.block, r.starts, r.sessions_left, r.seeds, r.values) for b in R.BASELINES}
    for m in (1, 2, 3):
        same = _with(same, "p16", f"net_month_{m}", lambda x: np.where(np.arange(2)[None, :] == 0, np.abs(x) + 1, x))
        same = _with(same, "p16", f"peak_month_{m}", lambda x: np.where(np.arange(2)[None, :] == 0, 0.0, x))
    v = _run(same)
    d = v.values["delta_star"]
    assert v.values["composite"]["ranking"][0] == "p16"
    assert not any(g["resolved"] for g in d["gaps"]) and d["spread"] > 0
    assert d["raw"] == pytest.approx(R.DELTA_FRACTION * d["spread"]) and d["how"].startswith("no gap resolved")
    assert d["value"] == max(R.DELTA_MIN, d["raw"])


def test_more_test_seeds_raise_the_power_and_leave_the_values(base) -> None:
    rs, v = base
    lo, hi = _run(rs, J=20), _run(rs, J=2000)
    assert hi.values["power"]["conjoint_lower"] >= lo.values["power"]["conjoint_lower"]
    assert lo.values["power"]["J_needed"] == hi.values["power"]["J_needed"]
    for k in ("budgets", "weights", "delta_star", "composite"):
        assert lo.values[k] == hi.values[k]


# ------------------------------------------------------------------------------- the document and the module agree
def _table(marker: str) -> list[list[str]]:
    text = DOC.read_text(encoding="utf-8")
    m = re.search(rf"<!-- {marker}:start -->(.*?)<!-- {marker}:end -->", text, re.S)
    assert m, f"the document has its {marker} table"
    rows = [ln for ln in m.group(1).strip().splitlines() if ln.startswith("|")][2:]
    return [[c.strip().strip("`") for c in r.strip("|").split("|")] for r in rows]


def test_the_documents_constants_are_the_modules() -> None:
    rows = {r[0]: r[1] for r in _table("wave42-constants")}
    assert set(rows) == set(R.CONSTANTS)
    for k, v in R.CONSTANTS.items():
        assert json.loads(rows[k]) == v, k


def test_the_documents_dimensions_and_limits_are_the_modules() -> None:
    dims = _table("wave42-dimensions")
    assert [(r[0], r[2], r[3], int(r[4]), r[5]) for r in dims] == \
        [(d.name, d.measure, d.key, d.horizon, "higher" if d.direction > 0 else "lower") for d in R.DIMENSIONS]
    lims = _table("wave42-limits")
    assert [(r[0], r[1], r[2], r[3], int(r[4]), r[5]) for r in lims] == \
        [(x.name, x.measure, x.key, x.direction, x.horizon, x.stat) for x in R.LIMITS]


def test_the_search_years_are_e208s_and_the_power_target_the_gates() -> None:
    charter = (ROOT / "CHARTER.md").read_text(encoding="utf-8")
    assert f"NQ {R.SEARCH_FIRST} to {R.SEARCH_LAST} (E-208)" in charter
    assert "NQ 2024-01-02 to 2026-07-16" in charter and R.HELD_OUT_FIRST == "2024-01-02"
    from extended.family_stats import MDL_POWER
    assert R.POWER_TARGET == MDL_POWER
    assert "next 13" in (ROOT / "CLAUDE.md").read_text(encoding="utf-8") and R.K_TEST == 13


def test_the_module_reads_no_file_and_imports_no_engine() -> None:
    tree = ast.parse((ROOT / "extended" / "wave42.py").read_text(encoding="utf-8"))
    mods = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    mods |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert mods <= {"__future__", "hashlib", "json", "math", "dataclasses", "typing", "numpy", "scipy",
                    "extended.family_stats"}, mods
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "open" not in calls
    assert "random" not in (ROOT / "extended" / "wave42.py").read_text(encoding="utf-8").replace(
        "draws randomness", "")
