"""Wave 4.2's setting rule (`docs/plans/WAVE42_SETTING_RULE.md`, `extended/wave42.py`), on synthetic baseline readings
only (no engine, no bar, no result file; fast). Corrective cycle 1 answers the red team's read
(`docs/reviews/WAVE42_RULE_2026-11-20.md`); its B-6 asked for tests that recompute every output from the readings:

- **recomputed** -- a reference written here from the text (`_reference`) recomputes, from the readings alone, the
  sessions left, the budgets, P_B and (24)'s states at B*, the caps, the weights, the composite, the gaps and their
  resolution, delta*, sigma, Q (by the per-unit sum of 2.2 (a) item 4, not by `q_factor`), each pair's delta and power,
  J_needed, and each limit with its headroom; hand-built units pin the bankroll stop and (24)'s three states;
- **bound** -- the input is H4's one output: its manifest's sha256, start days, seeds, optional measures, calendar
  and content digest, and no second application (B-1, B-2, m-6, m-9); J is the declared constant (B-3);
- **refusing** -- one test per refusal of the declaration's section 1, the held-out guard first;
- **moving as the text says** -- section 7's table, one test per row;
- **the document's constants, dimensions, weights and limits are the module's**, machine-read from its tables; the
  ledger is stated (B-8); the three-way note's 4.4 is E-230's form (B-7).
"""
from __future__ import annotations

import ast
import copy
import importlib.util
import inspect
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
NOTE = ROOT / "docs" / "plans" / "THREE_WAY_TEST_design.md"
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
FEE = 50.0                                   # a synthetic fee unit (the real one is read from the verified ledger)
J0 = R.H4_MIN_SEEDS                          # H4's synthetic seed count, at the declared minimum
NHO = 640                                    # a synthetic held-out session count (the real one: the pinned file's)
TEST_STARTS = {h: R.complete_starts(NHO, h) for h in R.HORIZONS}   # V-2: derived, never typed
SRC = {"file": R.HELD_OUT_CALENDAR, "sha256": R.HELD_OUT_CALENDAR_SHA256, "sessions": NHO}
H4SHA = "1" * 64


def _calendar(step: int = 2) -> tuple[str, ...]:
    """A synthetic search calendar: every `step`-th weekday from SEARCH_FIRST, SEARCH_LAST appended."""
    d = np.arange(np.datetime64(R.SEARCH_FIRST), np.datetime64(R.SEARCH_LAST) + np.timedelta64(1, "D"))
    days = [str(x) for x in d[np.is_busday(d)]][::step]
    return tuple(days if days[-1] == R.SEARCH_LAST else days + [R.SEARCH_LAST])


CAL = _calendar()
NC = len(CAL)
STARTS = CAL                                 # V-1: every session of the calendar is a start (H4's draft)
N = len(STARTS)


def _sl(starts=STARTS, cal=CAL) -> np.ndarray:
    pos = {d: i for i, d in enumerate(cal)}
    return np.asarray([len(cal) - pos[d] for d in starts])


def _reading(name: str, seed: int, *, pay: float, spend: float, J: int = J0, starts=STARTS,
             cal=CAL) -> R.BaselineReading:
    """One synthetic baseline: `pay` moves the payout odds and the months ahead, `spend` the fee multiples."""
    rng = np.random.default_rng(seed)
    n = len(starts)
    sl = _sl(starts, cal)
    paid = rng.random((n, J)) < pay
    passed = paid | (rng.random((n, J)) < 0.25)
    pass_days = np.where(passed, rng.integers(5, 90, (n, J)), R.W + 1).astype(float)
    days = np.where(paid, np.minimum(R.W, pass_days + rng.integers(1, 40, (n, J))), R.W + 1).astype(float)
    k6 = rng.integers(1, int(2 + 8 * spend), (n, J))
    x6 = (k6 * FEE).astype(float)
    x2 = np.where(passed, np.minimum(x6, rng.integers(1, 4, (n, J)) * FEE), x6).astype(float)
    v = {"spent_before_first_payout": x6, "first_payout_days": days, "first_pass_days": pass_days,
         "cash_to_first_pass": x2}
    for m in (1, 2, 3):
        v[f"net_month_{m}"] = rng.normal(400 * (pay - 0.5), 900, (n, J))
        v[f"peak_month_{m}"] = np.minimum(x6, FEE * rng.integers(1, 2 + 3 * m, (n, J))).astype(float)
    v["peak_oop_12_months"] = x6 + rng.integers(0, 4, (n, J)) * FEE
    v["share_months_positive"] = rng.integers(0, 13, (n, J)) / 12.0
    v["orders_max"] = rng.integers(1, 6, (n, J)).astype(float)
    v["accounts_max"] = rng.integers(1, 4, (n, J)).astype(float)
    v["taken_mean"] = rng.random((n, J)) * 3
    for key, (h, _, _) in R.REQUIRED.items():                   # blanks outside E_h are allowed (the blank rule)
        v[key] = np.asarray(v[key], dtype=float).copy()
        v[key][sl < h] = np.nan
    return R.BaselineReading(name, "search", R.READING, tuple(starts), tuple(range(J)), v)


PARAMS = {"naive_coin": (11, 0.35, 0.9), "p14": (12, 0.6, 0.4), "p15": (13, 0.55, 0.5), "p16": (14, 0.7, 0.3)}


def _readings(J: int = J0, **over) -> dict[str, R.BaselineReading]:
    p = dict(PARAMS)
    p.update(over)
    return {b: _reading(b, s, pay=a, spend=c, J=J) for b, (s, a, c) in p.items()}


def _manifest(rs, cal=CAL, **over) -> dict:
    """H4's manifest fields as its collection's sidecar records them for these readings (B-1, V-1)."""
    ref = rs["naive_coin"]
    man = {"sha256": H4SHA, "block": R.BLOCK, "reading": R.READING, "arm": R.ARM, **R.VERDICT, "W": R.W,
           "baselines": list(R.BASELINES), "starts": list(ref.starts), "seeds": list(ref.seeds),
           "calendar_sha256": R.calendar_digest(cal), "readings_sha256": R.readings_digest(rs)}
    man.update(over)
    return man


def _bind(rs, cal=CAL, **over) -> R.H4Binding:
    return R.H4Binding(H4SHA, _manifest(rs, cal, **over))


def _run(rs, *, h4=None, cal=CAL, starts=None, src=None, fee=FEE, fee_source=R.FEE_SOURCE) -> R.Wave42Values:
    return R.setting_rule(rs, h4=h4 if h4 is not None else _bind(rs), search_calendar=cal, fee_unit=fee,
                          fee_source=fee_source, test_starts=starts or TEST_STARTS,
                          test_starts_source=SRC if src is None else src)


def _with(rs, name, key, fn):
    """A copy of the readings with one baseline's measure replaced by fn(old)."""
    rs = dict(rs)
    b = rs[name]
    vals = dict(b.values)
    vals[key] = fn(np.asarray(vals[key], dtype=float).copy())
    rs[name] = R.BaselineReading(b.name, b.block, b.reading, b.starts, b.seeds, vals)
    return rs


def _retag(rs, name, **kw):
    rs = dict(rs)
    b = rs[name]
    f = {"block": b.block, "reading": b.reading, "starts": b.starts, "seeds": b.seeds, "values": b.values}
    f.update(kw)
    rs[name] = R.BaselineReading(b.name, f["block"], f["reading"], f["starts"], f["seeds"], f["values"])
    return rs


@pytest.fixture(scope="module")
def base():
    rs = _readings()
    return rs, _run(rs)


# --------------------------------------------------------------------------------- the reference, from the text
def _reference(rs, test_starts=TEST_STARTS, J=None) -> dict:
    """Every output recomputed from the readings by the declaration's words, independently of the module's code."""
    J = R.TEST_SEEDS if J is None else J
    BL = R.BASELINES
    sl = _sl(rs[BL[0]].starts)
    nJ = len(rs[BL[0]].seeds)
    V = {b: {k: np.asarray(x, dtype=float) for k, x in rs[b].values.items()} for b in BL}
    E = {h: sl >= h for h in (63, 126, 252)}
    ceil_fee = lambda x: FEE * max(1, math.ceil(x / FEE - 1e-9))   # noqa: E731
    x6 = np.concatenate([V[b]["spent_before_first_payout"][E[126]].ravel() for b in BL])
    out = {"budgets": [ceil_fee(np.quantile(x6, q)) for q in R.BUDGET_QUANTILES],
           "Bstar": ceil_fee(np.quantile(x6, 0.75))}
    Bs = out["Bstar"]
    raw = {}
    for b in BL:
        v = V[b]
        ahead = np.zeros_like(v["net_month_1"])
        for m in (1, 2, 3):
            ahead = ahead + ((v[f"net_month_{m}"] > 1e-6) & (v[f"peak_month_{m}"] <= Bs))
        raw[b] = {"money": ahead / 3, "bankroll": v["peak_oop_12_months"], "speed": v["first_payout_days"],
                  "cost": v["cash_to_first_pass"], "steady": v["share_months_positive"],
                  "ruin": (v["spent_before_first_payout"] > Bs).astype(float)}
    hz = {"money": 63, "bankroll": 252, "speed": 126, "cost": 126, "steady": 252, "ruin": 126}
    lower = {"bankroll", "speed", "cost", "ruin"}
    z, caps = {b: {} for b in BL}, {}
    for d in hz:
        r = E[hz[d]]
        if d in ("money", "steady", "ruin"):
            lo, hi = 0.0, 1.0
        else:
            if d == "cost":
                pool = np.concatenate([raw[b][d][r][(V[b]["first_pass_days"] <= R.W)[r]] for b in BL])
            else:
                pool = np.concatenate([raw[b][d][r].ravel() for b in BL])
            ql, qh = np.quantile(pool, 0.05), np.quantile(pool, 0.95)
            lo, hi = max(0.0, ql - 0.25 * (qh - ql)), qh + 0.25 * (qh - ql)
            if d == "speed":
                hi = min(hi, R.W + 1.0)
        caps[d] = (lo, hi)
        for b in BL:
            u = np.clip((raw[b][d] - lo) / (hi - lo), 0, 1)
            zz = 1 - u if d in lower else u
            if d == "cost":
                zz = np.where(V[b]["first_pass_days"] <= R.W, zz, 0.0)
            z[b][d] = zz
    out["caps"] = caps
    w = {d: 1 / len(hz) for d in hz}                           # equal weights (the lead's m-1 ruling)
    out["weights"] = w
    Cs = {b: sum(w[d] * z[b][d][E[hz[d]]].mean(axis=0) for d in hz) for b in BL}
    C = {b: float(Cs[b].mean()) for b in BL}
    order = sorted(BL, key=lambda b: (-C[b], BL.index(b)))
    out["C"], out["order"] = C, order
    gaps = []
    for a, b in zip(order, order[1:]):
        dd = Cs[a] - Cs[b]
        g, se = dd.mean(), dd.std(ddof=1) / math.sqrt(nJ)
        gaps.append((g, se, nJ >= 62 and g > 2.0 * se))
    spread = C[order[0]] - C[order[-1]]
    res = [g for g, _, ok in gaps if ok]
    rawd = min(res) if res else 0.25 * spread
    delta = min(0.05, max(0.01, rawd))
    out["gaps"], out["delta"] = gaps, delta
    best = order[0]
    r = E[252]
    unit = {b: sum(w[d] * z[b][d][r] for d in hz) for b in BL}
    sig = {}
    for b in BL:
        if b == best:
            s = math.sqrt(2) * math.sqrt(np.mean([np.var(unit[best][i], ddof=1) for i in range(unit[best].shape[0])]))
        else:
            dd = unit[best] - unit[b]
            s = math.sqrt(np.mean([np.var(dd[i], ddof=1) for i in range(dd.shape[0])]))
        sig[b] = min(1.0, s)
    out["sigma"] = sig
    deltas = {b: delta + C[best] - C[b] for b in BL}
    out["deltas"] = deltas
    Q1 = _q_by_units(w, hz, test_starts, 1)
    out["Q"] = Q1 / J
    alpha = 0.05 / (13 * 14)
    ch = math.sqrt(2 * math.log(1 / alpha))
    pp = lambda b, Q: stats.norm.cdf((deltas[b] / math.sqrt(Q) - ch) / sig[b])   # noqa: E731
    out["pair_power"] = {b: pp(b, out["Q"]) for b in BL}
    conj = lambda Q: max(0.0, 1 - sum(1 - pp(b, Q) for b in BL))                    # noqa: E731
    out["conjoint"] = conj(out["Q"])
    out["conj_at"] = lambda JJ: conj(Q1 / JJ)                                        # noqa: E731
    lims = {}
    present = list(R.LIMITS)                                   # every limit set (V-3 (a))
    zp = stats.norm.ppf(1 - 0.2 / len(present))
    for L in present:
        h = L.horizon
        if L.key == "not_paid_within_B":
            X = {b: 1.0 - ((V[b]["first_payout_days"] <= R.W) & (V[b]["spent_before_first_payout"] <= Bs))
                 for b in BL}
        else:
            X = {b: V[b][L.key] for b in BL}
        stat = (lambda x: float(np.mean(x))) if L.stat == "mean" else \
            (lambda x, p=float(L.stat[1:]) / 100: float(np.quantile(x, p)))
        M = {b: stat(X[b][E[h]]) for b in BL}
        sd = {b: float(np.std([stat(X[b][E[h]][:, c]) for c in range(nJ)], ddof=1)) for b in BL}
        ceil_ = L.direction == "ceiling"
        bb = min(BL, key=lambda b: ((M[b] if ceil_ else -M[b]), BL.index(b)))
        bw = min(BL, key=lambda b: ((-M[b] if ceil_ else M[b]), BL.index(b)))
        se = sd[bb] * math.sqrt(int(E[h].sum()) / (J * test_starts[h]))
        need = M[bb] + zp * se if ceil_ else M[bb] - zp * se
        val = max(M[bw], need) if ceil_ else min(M[bw], need)
        lims[L.name] = {"M": M, "se": se, "need": need, "value": val, "best": bb, "worst": bw}
    out["limits"], out["zp"] = lims, zp
    return out


def _q_by_units(w, hz, test_starts, J) -> float:
    """2.2 (a) item 4, unit by unit: each held-out unit (start i, seed c) moves the composite by at most
    a_u = sum over the dimensions whose E_h holds start i of w_d / (J n_{h_d}); Q = sum_u a_u^2 (so 4Q = sum c_u^2)."""
    n_max = max(test_starts[h] for h in set(hz.values()))
    total = 0.0
    for i in range(n_max):                     # start i is in E_h when i < n_h (the E_h nest)
        a = sum(w[d] / (J * test_starts[hz[d]]) for d in w if i < test_starts[hz[d]])
        total += J * a * a
    return total


# ------------------------------------------------------------------------------------------------ deterministic
def test_deterministic_and_order_free(base) -> None:
    rs, v = base
    again = _run(copy.deepcopy(rs))
    assert again.as_json() == v.as_json() and again.digest() == v.digest()
    rev = {k: rs[k] for k in reversed(list(rs))}
    assert _run(rev).digest() == v.digest()
    assert _run(list(rs.values()), h4=_bind(rs)).digest() == v.digest()
    json.loads(v.as_json())                                         # finite, canonical JSON


# ------------------------------------------------------------------------------------------- recomputed (B-6)
def test_sessions_left_are_computed_from_the_calendar_with_the_start_counted(base) -> None:
    """B-2: E_h holds the starts with at least h calendar sessions from the start (counted as session 1) to
    SEARCH_LAST; with every session a start, |E_h| is NC - h + 1 (the start exactly h from the end in, the next out)."""
    _, v = base
    for h in (63, 126, 252):
        assert v.values["search_starts"][str(h)] == NC - h + 1


def test_bankroll_states_on_hand_built_units() -> None:
    """MEASURES 2 and (24) at B = 100 on hand-built units: the stop at the peak (<= B counts, above B does not), the
    ahead tolerance, and (24)'s three states (paid within B, run out paid or unpaid, censored)."""
    B, W = 100.0, R.W
    one = lambda *x: np.asarray([x], dtype=float)                     # noqa: E731
    v = {"net_month_1": one(5, 5, 5, 5, 5), "peak_month_1": one(100, 101, 0, 0, 0),
         "net_month_2": one(5, 1e-7, -3, 5, 5), "peak_month_2": one(101, 0, 0, 0, 0),
         "net_month_3": one(1e-7, 5, 5, 5, 5), "peak_month_3": one(0, 0, 0, 100, 100.5),
         "spent_before_first_payout": one(100, 101, 50, 150, 100),
         "first_payout_days": one(40, 40, W + 1, W + 1, W)}
    s = R.bankroll_states(v, B)
    assert s["P_B"][0].tolist() == pytest.approx([1 / 3, 1 / 3, 2 / 3, 1.0, 2 / 3])
    assert s["run_out"].tolist() == [[0.0, 1.0, 0.0, 1.0, 0.0]]
    assert s["not_paid_within_B"].tolist() == [[0.0, 1.0, 1.0, 1.0, 0.0]]


def test_budgets_trace_to_the_pooled_spending_and_the_fee_lattice(base) -> None:
    rs, v = base
    ref = _reference(rs)
    b = v.values["budgets"]
    assert [t["budget"] for t in b["trace"]] == ref["budgets"]
    for t in b["trace"]:
        assert t["budget"] >= t["pooled_value"] and t["budget"] - t["pooled_value"] < FEE
    assert b["primary"] == ref["Bstar"] and b["fee_source"] == R.FEE_SOURCE
    assert b["values"] == sorted(set(b["values"]))
    assert len(set(ref["budgets"])) > 1 and ref["Bstar"] != ref["budgets"][0], "the synthetic budgets differ"


def test_caps_weights_and_composite_recomputed(base) -> None:
    rs, v = base
    ref = _reference(rs)
    dims = {d["name"]: d for d in v.values["dimensions"]}
    for name, (lo, hi) in ref["caps"].items():
        assert (dims[name]["lo"], dims[name]["hi"]) == pytest.approx((lo, hi)), name
    assert v.values["form"] == "composite"
    assert list(v.values["weights"]) == [d.name for d in R.DIMENSIONS]
    assert v.values["weights"] == pytest.approx(ref["weights"])
    assert v.values["composite"]["value"] == pytest.approx(ref["C"], abs=1e-12)
    assert v.values["composite"]["ranking"] == ref["order"]


def test_cost_scores_an_unpassed_unit_at_zero(base) -> None:
    """B-5: an unpassed unit's cost z is 0 whatever it spent; the caps come from the passed units only. A baseline
    whose units spend less but pass less does not gain on cost."""
    rs, v = base
    dims = {d["name"]: d for d in v.values["dimensions"]}
    sl = _sl()
    r = sl >= R.W
    for b in R.BASELINES:
        x = np.asarray(rs[b].values["cash_to_first_pass"])
        ok = np.asarray(rs[b].values["first_pass_days"]) <= R.W
        lo, hi = dims["cost"]["lo"], dims["cost"]["hi"]
        z = np.where(ok, 1 - np.clip((x - lo) / (hi - lo), 0, 1), 0.0)
        assert dims["cost"]["baseline_means"][b] == pytest.approx(float(z[r].mean()))
    cheap = _with(rs, "p15", "first_pass_days", lambda x: np.where(np.isnan(x), np.nan, R.W + 1.0))
    cheap = _with(cheap, "p15", "first_payout_days", lambda x: np.where(np.isnan(x), np.nan, R.W + 1.0))
    cheap = _with(cheap, "p15", "cash_to_first_pass", lambda x: np.where(np.isnan(x), np.nan, FEE))
    d2 = {d["name"]: d for d in _run(cheap).values["dimensions"]}["cost"]
    assert d2["baseline_means"]["p15"] == 0.0


def test_gaps_delta_star_and_power_recomputed(base) -> None:
    rs, v = base
    ref = _reference(rs)
    d, p = v.values["delta_star"], v.values["power"]
    assert [(g["gap"], g["se"], g["resolved"]) for g in d["gaps"]] == \
        [(pytest.approx(g), pytest.approx(se), ok) for g, se, ok in ref["gaps"]]
    assert d["value"] == pytest.approx(ref["delta"])
    assert p["pair_sigma"] == pytest.approx(ref["sigma"])
    assert p["pair_delta"] == pytest.approx(ref["deltas"])
    assert p["Q"] == pytest.approx(ref["Q"], rel=1e-12)
    assert p["pair_power"] == pytest.approx(ref["pair_power"])
    assert p["conjoint_lower"] == pytest.approx(ref["conjoint"])
    assert p["test_seeds"] == R.TEST_SEEDS
    assert len({round(x, 9) for x in ref["deltas"].values()}) == 4, "each pair's delta differs"
    Jn = p["J_needed"]
    assert Jn is not None
    assert ref["conj_at"](Jn) >= R.POWER_TARGET and (Jn == 1 or ref["conj_at"](Jn - 1) < R.POWER_TARGET)


@pytest.mark.parametrize("hs", [(63, 252), (63, 126, 252), (126, 252)])
def test_q_factor_is_the_per_unit_sum_on_nested_horizons(hs) -> None:
    w = {f"d{i}": x for i, x in enumerate((0.4, 0.3, 0.2, 0.1)[:len(hs) + 1])}
    hz = {f"d{i}": hs[min(i, len(hs) - 1)] for i in range(len(hs) + 1)}
    starts = {63: 601, 126: 538, 252: 412}
    for J in (1, 7, 40):
        assert R.q_factor(w, hz, starts, J) == pytest.approx(_q_by_units(w, hz, starts, J), rel=1e-12)


def test_power_formula_is_the_three_way_notes_on_one_horizon() -> None:
    alpha, n, J, delta, sig = R.level(13), 500, 40, 0.02, 0.6
    Q = R.q_factor({"a": 0.5, "b": 0.5}, {"a": 63, "b": 63}, {63: n}, J)
    assert Q == pytest.approx(1 / (J * n))
    ch = math.sqrt(2 * math.log(1 / alpha))
    assert R.pair_power(delta, Q, sig, alpha) == pytest.approx(stats.norm.cdf((math.sqrt(J * n) * delta - ch) / sig))
    assert R.pair_power(delta, Q, 0.0, alpha) in (0.0, 1.0)


def test_limits_recomputed_with_the_joint_headroom(base) -> None:
    rs, v = base
    ref = _reference(rs)
    lims = {x["name"]: x for x in v.values["limits"]["values"]}
    assert v.values["limits"]["headroom_z"] == pytest.approx(ref["zp"])
    assert ref["zp"] > stats.norm.ppf(R.POWER_TARGET)               # joint over the six limits set (m-3 (c))
    for name, L in ref["limits"].items():
        got = lims[name]
        assert got["baseline_values"] == pytest.approx(L["M"]), name
        assert got["best_se_test"] == pytest.approx(L["se"]), name
        assert got["headroom_needed"] == pytest.approx(L["need"]), name
        assert got["value"] == pytest.approx(L["value"]), name
        assert (got["best"], got["worst"]) == (L["best"], L["worst"]), name
    assert lims["not_paid_within_B"]["budget"] == v.values["budgets"]["primary"]
    assert v.values["limits"]["check_level"] == R.LIMIT_CHECK_LEVEL
    assert "point estimate governs" in v.values["limits"]["form"]


def test_each_limit_prints_its_search_year_estimates(base) -> None:
    """m-3 (b): each baseline's estimate per search year of its start days, beside each limit."""
    rs, v = base
    L = {x["name"]: x for x in v.values["limits"]["values"]}["first_payout_days_p50"]
    sl = _sl()
    yrs = np.asarray([d[:4] for d in STARTS])
    x = np.asarray(rs["p14"].values["first_payout_days"])
    for y in ("2020", "2021", "2022", "2023"):
        sel = (sl >= R.W) & (yrs == y)
        assert L["by_search_year"]["p14"][y] == pytest.approx(float(np.quantile(x[sel], 0.5)))


def test_a_days_limit_at_the_window_end_is_vacuous(base) -> None:
    """m-3 (a): every baseline's median first payout beyond the window: the ceiling W + 1 is flagged vacuous."""
    rs, _ = base
    late = rs
    for b in R.BASELINES:
        late = _with(late, b, "first_payout_days", lambda x: np.where(np.isnan(x), np.nan, R.W + 1.0))
    L = {x["name"]: x for x in _run(late).values["limits"]["values"]}["first_payout_days_p50"]
    assert L["value"] == R.W + 1.0 and L["vacuous"] and "a priori" in L["vacuous_reason"]


def test_input_digest_moves_with_any_input(base) -> None:
    rs, v = base
    d0 = v.values["input_sha256"]
    assert _run(_with(rs, "p15", "net_month_2", lambda x: x + 1e-3)).values["input_sha256"] != d0
    assert _run(rs, fee=FEE + 1).values["input_sha256"] != d0
    n2 = NHO + 1
    assert _run(rs, starts={h: R.complete_starts(n2, h) for h in R.HORIZONS},
                src={**SRC, "sessions": n2}).values["input_sha256"] != d0


def _digest_by_hand(rs) -> str:
    """The readings' digest from its declared byte layout, written here apart from `readings_digest` (R3-4): per
    baseline in name order, the JSON of [name, block, reading, starts, seeds, sorted keys], then per key in order its
    name, the JSON of its shape, and its little-endian float64 bytes with every blank one canonical NaN."""
    import hashlib

    h = hashlib.sha256()
    for name in sorted(rs):
        b = rs[name]
        h.update(json.dumps([b.name, b.block, b.reading, list(map(str, b.starts)), list(map(int, b.seeds)),
                             sorted(b.values)]).encode("utf-8"))
        for key in sorted(b.values):
            x = np.array(b.values[key], dtype="<f8", copy=True)
            x[np.isnan(x)] = float("nan")
            h.update(key.encode("utf-8") + json.dumps(list(x.shape)).encode("utf-8") + x.tobytes(order="C"))
    return h.hexdigest()


def test_the_readings_digest_is_its_declared_layout_and_sees_every_matrix_and_seed(base) -> None:
    """R3-4: the digest equals the hand-written layout, and a one-cell change to any required matrix, or a one-seed
    change, moves it."""
    rs, _ = base
    d0 = R.readings_digest(rs)
    assert d0 == _digest_by_hand(rs)
    for key in R.REQUIRED:
        h = int(np.argmax(_sl() >= R.REQUIRED[key][0]))
        moved = _with(rs, "p15", key, lambda x, h=h: np.where((np.arange(N) == h)[:, None] & (np.arange(J0) == 0)[None, :],
                                                             x + 1.0, x))
        assert R.readings_digest(moved) != d0, key
    assert R.readings_digest(_retag(rs, "p16", seeds=(J0,) + rs["p16"].seeds[1:])) != d0


def test_input_digest_covers_h4s_manifest(base) -> None:
    """V-1's audit chain (m2-4): a manifest field that no other check reads still moves input_sha256."""
    rs, v = base
    extra = _run(rs, h4=_bind(rs, writer_note="another sidecar")).values
    assert extra["input_sha256"] != v.values["input_sha256"]
    assert extra["budgets"] == v.values["budgets"] and extra["limits"] == v.values["limits"]


# ------------------------------------------------------------------------------------------- bound (B-1, B-3)
def test_the_output_names_h4s_one_output_and_the_ledger(base) -> None:
    rs, v = base
    h = v.values["h4"]
    assert h["result_sha256"] == H4SHA and h["readings_sha256"] == R.readings_digest(rs)
    assert h["calendar_sha256"] == R.calendar_digest(CAL) and h["starts"] == N and h["seeds"] == J0
    assert v.values["held_out_read_ledger"]["entry"] == R.HELD_OUT_LEDGER
    assert v.values["held_out_read_ledger"]["sha256"] == R.HELD_OUT_CALENDAR_SHA256
    assert v.values["h4"]["arm"] == R.ARM and v.values["h4"]["verdict"] == R.VERDICT
    assert "nominal" in v.values["held_out_read_ledger"]["level"]


def test_the_function_takes_no_application_list() -> None:
    """V-1: a second application is refused by the script's existing output file (`tests/test_wave42_apply.py`), not
    by a list the caller passes: the function has no such parameter."""
    params = set(inspect.signature(R.setting_rule).parameters)
    assert "prior_applications" not in params
    assert params == {"readings", "h4", "search_calendar", "fee_unit", "fee_source", "test_starts", "test_starts_source"}


def _subset(rs, rows=None, cols=None):
    out = {}
    for k, b in rs.items():
        r = slice(None) if rows is None else rows
        c = slice(None) if cols is None else cols
        st = tuple(np.asarray(b.starts)[r].tolist())
        sd = tuple(np.asarray(b.seeds)[c].tolist())
        out[k] = R.BaselineReading(b.name, b.block, b.reading, st, sd,
                                   {x: np.asarray(y)[r][:, c] for x, y in b.values.items()})
    return out


def test_a_subset_of_h4s_output_is_refused(base) -> None:
    """B-1: the first half of the start days, the first two seeds, or a dropped optional measure, under H4's own
    manifest, are refused; so is a manifest whose content digest is not the readings'."""
    rs, _ = base
    h4 = _bind(rs)
    with pytest.raises(R.Wave42Refused, match="every start day H4 declared"):
        _run(_subset(rs, rows=slice(0, N // 2)), h4=h4)
    with pytest.raises(R.Wave42Refused, match="every seed H4 declared"):
        _run(_subset(rs, cols=slice(0, 2)), h4=h4)
    gone = {k: R.BaselineReading(b.name, b.block, b.reading, b.starts, b.seeds,
                                 {x: y for x, y in b.values.items() if x != "accounts_max"}) for k, b in rs.items()}
    with pytest.raises(R.Wave42Refused, match="required"):
        _run(gone, h4=h4)
    with pytest.raises(R.Wave42Refused, match="readings_sha256"):
        _run(_with(rs, "p14", "net_month_1", lambda x: x + 1.0), h4=h4)


@pytest.mark.parametrize("field,value,match", [
    ("sha256", "2" * 64, "another result file"),
    ("block", "held_out", "block's"),
    ("reading", "as_walked", "block's"),
    ("arm", "worse_1", "arm under the verdict"),
    ("arm", "missed_0.1", "arm under the verdict"),
    ("denial", 0.25, "arm under the verdict"),
    ("placement", "on", "arm under the verdict"),
    ("focused_trader", "on", "arm under the verdict"),
    ("W", 125, "integer W"),
    ("W", "126", "integer W"),
    ("W", 126.9, "integer W"),
    ("W", 126.0, "integer W"),
    ("W", [126, 252], "integer W"),
    ("W", True, "integer W"),
    ("baselines", ["naive_coin", "p14", "p15"], "declares the baselines"),
    ("calendar_sha256", "3" * 64, "calendar is not the one"),
])
def test_a_manifest_that_is_not_h4s_is_refused(base, field, value, match) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match=match):
        _run(rs, h4=_bind(rs, **{field: value}))


def test_a_manifest_missing_a_field_or_an_unnamed_file_is_refused(base) -> None:
    rs, _ = base
    man = dict(_bind(rs).manifest)
    man.pop("readings_sha256")
    with pytest.raises(R.Wave42Refused, match="lacks"):
        _run(rs, h4=R.H4Binding(H4SHA, man))
    with pytest.raises(R.Wave42Refused, match="64 hex"):
        _run(rs, h4=R.H4Binding("not a sha", dict(_bind(rs).manifest)))


def test_j_is_the_declared_constant_and_moves_only_the_headroom_and_the_power(base, monkeypatch) -> None:
    """B-3: the rule takes no J; the declared TEST_SEEDS scales each headroom by 1 / sqrt(J) and moves the power;
    budgets, weights, the composite and delta* do not move."""
    rs, v = base
    assert not {"test_seeds", "J", "seeds"} & set(inspect.signature(R.setting_rule).parameters)
    monkeypatch.setattr(R, "TEST_SEEDS", 4 * R.TEST_SEEDS)
    v4 = _run(rs)
    for k in ("budgets", "weights", "delta_star", "composite"):
        assert v4.values[k] == v.values[k]
    a = {x["name"]: x for x in v.values["limits"]["values"]}
    b = {x["name"]: x for x in v4.values["limits"]["values"]}
    for name in a:
        if a[name]["status"] == "set" and a[name]["best_se_test"] > 0:
            assert b[name]["best_se_test"] == pytest.approx(a[name]["best_se_test"] / 2)
    assert v4.values["power"]["conjoint_lower"] >= v.values["power"]["conjoint_lower"]
    assert v4.values["power"]["Q"] == pytest.approx(v.values["power"]["Q"] / 4)


def test_the_declared_j_covers_the_worst_case_with_margin() -> None:
    """m2-2: TEST_SEEDS is the lead's choice; beside it, the worst case's need (delta* = DELTA_MIN against four
    baselines equal to the best, sigma 1, the declared equal weights) at the held-out complete starts' upper bounds
    (`three_way_arith`) and at 40 fewer sessions: TEST_SEEDS is at least 1.5 times the need at k = 13, and covers
    the need at every k from 13 to 17."""
    spec = importlib.util.spec_from_file_location("three_way_arith_w42", ARITH)
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    wh = A.weekdays(*A.HELD_OUT)
    w = {d.name: 1 / len(R.DIMENSIONS) for d in R.DIMENSIONS}
    hz = {d.name: d.horizon for d in R.DIMENSIONS}
    floor = {b: R.DELTA_MIN for b in R.BASELINES}
    ones = {b: 1.0 for b in R.BASELINES}
    for n in (wh, wh - 40):
        starts = {h: R.complete_starts(n, h) for h in (63, 126, 252)}
        assert starts == {h: A.complete_starts(n, h) for h in (63, 126, 252)}
        for k in range(13, 18):
            need = R.j_needed(floor, ones, w, hz, starts, R.level(k))
            assert need is not None and R.TEST_SEEDS >= (1.5 * need if k == 13 else need), (n, k, need)


def test_the_output_prints_the_worst_case_beside_the_declared_j(base) -> None:
    _, v = base
    p = v.values["power"]
    w = v.values["weights"]
    hz = {d.name: d.horizon for d in R.DIMENSIONS}
    assert p["J_worst_case"] == R.j_needed({b: R.DELTA_MIN for b in R.BASELINES}, {b: 1.0 for b in R.BASELINES},
                                           w, {k: hz[k] for k in w}, TEST_STARTS, R.level(R.K_TEST))
    assert p["J_worst_case"] <= R.TEST_SEEDS


def test_appendix_as_h7_row_runs_the_declared_j() -> None:
    """m2-2: the three-way note's Appendix A sizes the held-out test at W42-R1's TEST_SEEDS."""
    spec = importlib.util.spec_from_file_location("three_way_arith_w42h", ARITH)
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    h7 = [r for r in A.parts() if r[0] == "H7 held-out, Hoeffding"]
    assert len(h7) == 1 and h7[0][3] == R.TEST_SEEDS == A.W42_TEST_SEEDS


# --------------------------------------------------------------------------------------------------- refusing
@pytest.mark.parametrize("tag", ["held_out", "heldout", "held-out", "confirmation", "Search", ""])
def test_refuses_a_held_out_tag(base, tag) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="block"):
        _run(_retag(rs, "p16", block=tag), h4=_bind(rs))


def test_the_held_out_guard_comes_before_everything(base) -> None:
    """A held-out tag is refused even with every other input wrong (the guard runs first)."""
    rs, _ = base
    bad = _retag(rs, "p16", block="held_out")
    with pytest.raises(R.Wave42Refused, match="only the search years"):
        R.setting_rule(bad, h4=None, search_calendar=(), fee_unit=-1, fee_source="", test_starts={},
                       test_starts_source={})


@pytest.mark.parametrize("day", ["2024-01-02", "2025-06-02", "2026-07-17", "2019-12-31"])
def test_refuses_a_start_day_outside_the_search_years(base, day) -> None:
    rs, _ = base
    starts = list(rs["p14"].starts)
    starts[-1] = day
    with pytest.raises(R.Wave42Refused, match="search years"):
        _run(_retag(rs, "p14", starts=tuple(starts)), h4=_bind(rs))


def test_refuses_another_reading(base) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="martingale_outcome"):
        _run(_retag(rs, "p15", reading="as_walked"), h4=_bind(rs))


def test_refuses_a_wrong_baseline_set(base) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="exactly"):
        _run({k: rs[k] for k in ("naive_coin", "p14", "p15")}, h4=_bind(rs))
    swapped = {**rs, "p15": R.BaselineReading("p14", *[getattr(rs["p15"], f) for f in
                                                       ("block", "reading", "starts", "seeds", "values")])}
    with pytest.raises(R.Wave42Refused, match="exactly"):
        _run(swapped, h4=_bind(rs))


@pytest.mark.parametrize("cal", [CAL[1:], CAL[:-1], CAL[:5] + CAL[4:], tuple(reversed(CAL)), ()])
def test_refuses_a_calendar_that_is_not_the_search_years(base, cal) -> None:
    """B-2: refused by the calendar's own check, the manifest naming that same calendar (so no later check fires)."""
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="strictly increasing from"):
        _run(rs, cal=cal, h4=_bind(rs, calendar_sha256=R.calendar_digest(cal)))


def test_refuses_a_start_not_on_the_calendar(base) -> None:
    rs, _ = base
    sat = "2021-06-05"                                     # a Saturday inside the search years
    i = next(k for k, d in enumerate(STARTS) if d > sat)
    st = STARTS[:i - 1] + (sat,) + STARTS[i:]
    moved = {k: R.BaselineReading(b.name, b.block, b.reading, st, b.seeds, b.values) for k, b in rs.items()}
    with pytest.raises(R.Wave42Refused, match="not a session of the search calendar"):
        _run(moved)


def test_refuses_starts_that_are_not_every_session() -> None:
    """V-1's hardening: a start set short of the whole calendar is refused whoever built the manifest."""
    rs = _readings()
    cut = _subset(rs, rows=slice(1, None))
    with pytest.raises(R.Wave42Refused, match="every session of the search calendar"):
        _run(cut)


def test_refuses_seeds_that_are_not_the_indices() -> None:
    rs = _readings()
    shifted = {k: R.BaselineReading(b.name, b.block, b.reading, b.starts, tuple(s + 1 for s in b.seeds), b.values)
               for k, b in rs.items()}
    with pytest.raises(R.Wave42Refused, match="seed indices 0 to J - 1"):
        _run(shifted)


def test_refuses_unpaired_readings(base) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="paired"):
        _run(_retag(rs, "p15", seeds=tuple(s + 100 for s in rs["p15"].seeds)))
    st = list(STARTS)
    st[3] = "2020-03-07"                                   # one start day moved to another date
    with pytest.raises(R.Wave42Refused, match="paired"):
        _run(_retag(rs, "p16", starts=tuple(st)))


def test_refuses_one_seed_or_repeated_seeds() -> None:
    with pytest.raises(R.Wave42Refused, match="at least two"):
        _run(_readings(J=1))
    rs = _readings()
    dup = {k: R.BaselineReading(b.name, b.block, b.reading, b.starts, (2,) + b.seeds[1:], b.values)
           for k, b in rs.items()}
    with pytest.raises(R.Wave42Refused, match="distinct"):
        _run(dup)


def test_refuses_start_days_out_of_order(base) -> None:
    rs, _ = base
    st = list(STARTS)
    st[2], st[3] = st[3], st[2]
    moved = {k: R.BaselineReading(b.name, b.block, b.reading, tuple(st), b.seeds, b.values) for k, b in rs.items()}
    with pytest.raises(R.Wave42Refused, match="strictly increasing"):
        _run(moved)


@pytest.mark.parametrize("fee,source,match", [(0.0, R.FEE_SOURCE, "positive"), (float("nan"), R.FEE_SOURCE, "positive"),
                                             (FEE, "", "Standard path"), (FEE, "a typed figure", "Standard path")])
def test_refuses_a_fee_unit_without_its_ledger_source(base, fee, source, match) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match=match):
        _run(rs, fee=fee, fee_source=source)


@pytest.mark.parametrize("starts", [{63: 578, 126: 515}, {63: 578, 126: 515, 252: 390},
                                    {63: 579, 126: 515, 252: 389}, {63: 578, 126: 515, 252: 0}])
def test_refuses_bad_test_start_counts(base, starts) -> None:
    """V-2: the counts are complete_starts of the held-out calendar's sessions, at every horizon."""
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="complete-start count|complete_starts"):
        _run(rs, starts=starts)


def test_refuses_a_held_out_calendar_too_short_for_a_horizon(base) -> None:
    """A held-out calendar of 200 sessions has no complete 252-session start: the counts, though complete_starts of
    it, are refused for not being positive."""
    rs, _ = base
    n = 200
    with pytest.raises(R.Wave42Refused, match="counts are positive"):
        _run(rs, starts={h: R.complete_starts(n, h) for h in R.HORIZONS}, src={**SRC, "sessions": n})


@pytest.mark.parametrize("src", [{}, {**SRC, "file": "another_calendar.csv"}, {**SRC, "sha256": "0" * 64},
                                 {**SRC, "sessions": "640"}, {**SRC, "sessions": 0},
                                 {k: v for k, v in SRC.items() if k != "sha256"}])
def test_refuses_test_counts_without_their_source(base, src) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="pinned held-out calendar"):
        _run(rs, src=src)


def test_refuses_malformed_measures(base) -> None:
    rs, _ = base
    with pytest.raises(R.Wave42Refused, match="blank"):
        _run(_with(rs, "p14", "first_payout_days", lambda x: np.where(np.arange(N)[:, None] == 0, np.nan, x)))
    with pytest.raises(R.Wave42Refused, match="a priori"):
        _run(_with(rs, "p14", "share_months_positive", lambda x: x + 2.0))
    with pytest.raises(R.Wave42Refused, match="start days x seeds"):
        _run(_with(rs, "p14", "taken_mean", lambda x: x[:, :-1]))
    with pytest.raises(R.Wave42Refused, match="paid before its first pass"):
        _run(_with(rs, "p14", "first_pass_days", lambda x: np.where(np.isnan(x), np.nan, R.W + 1.0)))
    b = rs["p16"]
    for key in ("cash_to_first_pass", "first_pass_days", "orders_max", "accounts_max", "taken_mean"):
        part = {**rs, "p16": R.BaselineReading(b.name, b.block, b.reading, b.starts, b.seeds,
                                               {k: x for k, x in b.values.items() if k != key})}
        with pytest.raises(R.Wave42Refused, match="required"):
            _run(part)


def test_refuses_an_empty_horizon() -> None:
    """A search calendar of 50 sessions: no start has 63 sessions left, so E_63 is empty."""
    short = CAL[:49] + (R.SEARCH_LAST,)
    rs = {b: _reading(b, s, pay=a, spend=c, starts=short, cal=short) for b, (s, a, c) in PARAMS.items()}
    with pytest.raises(R.Wave42Refused, match="E_63 is empty"):
        _run(rs, cal=short, h4=_bind(rs, cal=short))


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
    assert L2["value"] == pytest.approx(L0["value"])
    assert L2["baseline_values"][L0["best"]] < L0["baseline_values"][L0["best"]]


def test_equal_baselines_set_the_limit_at_the_headroom(base) -> None:
    """Every baseline equal on supply (a floor): the worst is the best, so the headroom binds, below it by the joint
    z times se_test, se_test the best's per-seed sd times sqrt(|E_h search| / (J n_h test))."""
    rs, _ = base
    same = dict(rs)
    for b in R.BASELINES:
        same = _with(same, b, "taken_mean", lambda x: np.asarray(rs["p14"].values["taken_mean"], dtype=float))
    v = _run(same)
    L = {x["name"]: x for x in v.values["limits"]["values"]}["taken_mean_p10"]
    M = L["baseline_values"]["p14"]
    sl = _sl()
    x = np.asarray(rs["p14"].values["taken_mean"])[sl >= R.W]
    sd = float(np.std([np.quantile(x[:, c], 0.1) for c in range(J0)], ddof=1))
    se = sd * math.sqrt(int((sl >= R.W).sum()) / (R.TEST_SEEDS * TEST_STARTS[R.W]))
    assert L["best_se_test"] == pytest.approx(se) and se > 0
    assert L["binds"] == "headroom" and L["value"] < M
    assert L["value"] == pytest.approx(M - R.limit_z(6) * se)


def test_every_limit_is_set() -> None:
    """V-3 (a): the three workload and supply measures are required, so all six limits are set."""
    assert all(not L.optional for L in R.LIMITS)
    assert {"orders_max", "accounts_max", "taken_mean"} <= set(R.REQUIRED)


def test_cost_counts_a_pass_on_session_w(base) -> None:
    """m2-4: a unit that passes on session W (first_pass_days = W) is passed; its cost z is its cash's, not zero."""
    rs, _ = base
    at_w = _with(rs, "p15", "first_pass_days", lambda x: np.where(np.isnan(x), np.nan, float(R.W)))
    at_w = _with(at_w, "p15", "first_payout_days", lambda x: np.where(np.isnan(x), np.nan, R.W + 1.0))
    d = {x["name"]: x for x in _run(at_w).values["dimensions"]}["cost"]
    r = _sl() >= R.W
    x = np.asarray(at_w["p15"].values["cash_to_first_pass"])[r]
    z = 1 - np.clip((x - d["lo"]) / (d["hi"] - d["lo"]), 0, 1)
    assert d["baseline_means"]["p15"] == pytest.approx(float(z.mean())) and z.mean() > 0


def test_cost_caps_count_passes_on_session_w(base) -> None:
    """m2-4, the caps' side: every unit of every baseline passes on session W, so cost's caps are the widened 5-95 %
    quantiles of all their cash on E_W (not the degenerate caps of no unit passed)."""
    rs, _ = base
    at_w = rs
    for b in R.BASELINES:
        at_w = _with(at_w, b, "first_pass_days", lambda x: np.where(np.isnan(x), np.nan, float(R.W)))
        at_w = _with(at_w, b, "first_payout_days", lambda x: np.where(np.isnan(x), np.nan, R.W + 1.0))
    d = {x["name"]: x for x in _run(at_w).values["dimensions"]}["cost"]
    r = _sl() >= R.W
    pool = np.concatenate([np.asarray(at_w[b].values["cash_to_first_pass"])[r].ravel() for b in R.BASELINES])
    ql, qh = np.quantile(pool, 0.05), np.quantile(pool, 0.95)
    assert (d["lo"], d["hi"]) == pytest.approx((max(0.0, ql - 0.25 * (qh - ql)), qh + 0.25 * (qh - ql)))
    assert d["share_passed_by_W"] == 1.0


def test_a_limit_beyond_every_baseline_unit_is_flagged_vacuous(base) -> None:
    """m2-4: every unit's busiest day at three orders: the p90 ceiling sits on the last unit, flagged vacuous for it."""
    rs, _ = base
    same = rs
    for b in R.BASELINES:
        same = _with(same, b, "orders_max", lambda x: np.where(np.isnan(x), np.nan, 3.0))
    L = {x["name"]: x for x in _run(same).values["limits"]["values"]}["orders_max_p90"]
    assert L["value"] == 3.0 and L["vacuous"] and "beyond every baseline unit" in L["vacuous_reason"]


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


def test_a_dimension_that_moves_with_another_is_kept_and_the_weights_stay(base) -> None:
    """B-4: cost made a monotone function of speed (Spearman's rho 1): no dimension is dropped; the six declared
    weights stand and rho is reported beside, deciding nothing. A strong negative rho changes nothing either."""
    rs, v0 = base
    red = dict(rs)
    for b in R.BASELINES:
        days = np.asarray(rs[b].values["first_payout_days"], dtype=float)
        red = _with(red, b, "cash_to_first_pass", lambda x, d=days: np.where(np.isnan(x), np.nan, 10.0 * d))
    v = _run(red)
    assert v.values["form"] == "composite"
    assert v.values["weights"] == v0.values["weights"]
    assert list(v.values["weights"].values()) == pytest.approx([1 / len(R.DIMENSIONS)] * len(R.DIMENSIONS))
    assert all(d["weight"] > 0 for d in v.values["dimensions"])
    assert "speed|cost" in v.values["rho_beside"]


def _flat(seed: int, share_good: float) -> R.BaselineReading:
    """Every dimension but money constant over every unit (nobody passes, nobody is paid, the same spend)."""
    rng = np.random.default_rng(seed)
    sl = _sl()
    good = rng.random((N, J0)) < share_good
    v = {"spent_before_first_payout": np.full((N, J0), 4 * FEE), "first_payout_days": np.full((N, J0), R.W + 1.0),
         "first_pass_days": np.full((N, J0), R.W + 1.0), "cash_to_first_pass": np.full((N, J0), 4 * FEE),
         "peak_oop_12_months": np.full((N, J0), 4 * FEE), "share_months_positive": np.zeros((N, J0)),
         "orders_max": np.ones((N, J0)), "accounts_max": np.ones((N, J0)), "taken_mean": np.ones((N, J0))}
    for m in (1, 2, 3):
        v[f"net_month_{m}"] = np.where(good, 100.0, -100.0)
        v[f"peak_month_{m}"] = np.full((N, J0), FEE)
    for key, (h, _, _) in R.REQUIRED.items():
        v[key] = np.asarray(v[key], dtype=float).copy()
        v[key][sl < h] = np.nan
    return R.BaselineReading("x", "search", R.READING, STARTS, tuple(range(J0)), v)


def test_every_other_dimension_constant_gives_the_fallback() -> None:
    rs = {}
    for i, b in enumerate(R.BASELINES):
        r = _flat(21 + i, 0.5 + 0.05 * i)
        rs[b] = R.BaselineReading(b, r.block, r.reading, r.starts, r.seeds, r.values)
    v = _run(rs)
    assert v.values["form"] == "fallback" and v.values["weights"] == {"money": 1.0}
    assert all(d["constant"] for d in v.values["dimensions"][1:]) and not v.values["dimensions"][0]["constant"]
    assert v.values["null_journeys"]["composite"]["do_nothing"] == 0.0     # the fallback reads P_B alone


def test_the_null_journeys_and_the_floor(base) -> None:
    """V-4: beside the baselines, the do-nothing journey scores exactly bankroll's and ruin's weights (2/6: z = 1 on
    both, 0 on the rest) and the one-evaluation quitter is recomputed from the caps; the do-nothing composite is the
    declared floor, and the guards are named."""
    rs, v = base
    nj = v.values["null_journeys"]
    assert nj["composite"]["do_nothing"] == pytest.approx(2 / 6)
    assert nj["floor"]["value"] == nj["composite"]["do_nothing"] and "exceed" in nj["floor"]["rule"]
    dims = {d["name"]: d for d in v.values["dimensions"]}
    fee, Bs = FEE, v.values["budgets"]["primary"]
    zb = 1 - min(1.0, max(0.0, (fee - dims["bankroll"]["lo"]) / (dims["bankroll"]["hi"] - dims["bankroll"]["lo"])))
    zr = 0.0 if fee > Bs else 1.0
    assert nj["composite"]["quit_at_first_failure"] == pytest.approx((zb + zr) / 6)
    C = v.values["composite"]["value"]
    assert nj["baselines_at_or_below_floor"] == [b for b in R.BASELINES if C[b] <= 2 / 6 + 1e-12]
    g = v.values["inactivity_guards"]
    lim = {x["name"]: x for x in v.values["limits"]["values"]}["not_paid_within_B"]
    assert g["not_paid_within_B"] == ("live" if not lim["vacuous"] else g["not_paid_within_B"])
    assert "3.8 (c)" in g["long_run_gate"]


def test_a_vacuous_not_paid_limit_names_the_long_run_gate_alone(base) -> None:
    """V-4: if no baseline is ever paid within B* by W, the limit is 1, vacuous, and the output says only the
    long-run gate stops a quitter."""
    rs, _ = base
    never = rs
    for b in R.BASELINES:
        never = _with(never, b, "first_payout_days", lambda x: np.where(np.isnan(x), np.nan, R.W + 1.0))
    g = _run(never).values["inactivity_guards"]
    assert g["not_paid_within_B"].startswith("vacuous") and "long-run gate" in g["not_paid_within_B"]


def test_one_varying_dimension_besides_money_keeps_the_composite() -> None:
    rs = {}
    for i, b in enumerate(R.BASELINES):
        r = _flat(21 + i, 0.5 + 0.05 * i)
        rs[b] = R.BaselineReading(b, r.block, r.reading, r.starts, r.seeds, r.values)
    rs = _with(rs, "p16", "share_months_positive", lambda x: np.where(np.isnan(x), np.nan, 0.5))
    v = _run(rs)
    assert v.values["form"] == "composite" and len(v.values["weights"]) == len(R.DIMENSIONS)


def test_identical_baselines_put_delta_star_at_its_floor(base) -> None:
    rs, _ = base
    p = rs["p14"]
    same = {b: R.BaselineReading(b, p.block, p.reading, p.starts, p.seeds, p.values) for b in R.BASELINES}
    v = _run(same)
    d = v.values["delta_star"]
    assert all(not g["resolved"] and g["gap"] == 0 for g in d["gaps"])
    assert d["spread"] == 0 and d["value"] == R.DELTA_MIN and "floor" in d["how"]
    assert v.values["composite"]["ranking"] == list(R.BASELINES)          # ties broken in the declared order


def _planted(steady: dict[str, np.ndarray], J: int = J0) -> dict[str, R.BaselineReading]:
    """Four copies of P-14's reading that differ only in the steady share, set per seed (the same on every unit), so
    each pair's per-seed composite difference is the steady weight times the planted difference."""
    p = _readings(J=J)["p14"]
    rs = {b: R.BaselineReading(b, p.block, p.reading, p.starts, p.seeds, p.values) for b in R.BASELINES}
    for b, s in steady.items():
        rs = _with(rs, b, "share_months_positive", lambda x, s=s: np.where(np.isnan(x), np.nan, s[None, :] + 0 * x))
    return rs


def _standard(seed: int, J: int = J0) -> np.ndarray:
    e = np.random.default_rng(seed).standard_normal(J)
    return (e - e.mean()) / e.std(ddof=1)                  # mean 0, sample sd 1


def _ladder(J: int, top_ratio: float, seed: int = 5) -> dict[str, R.BaselineReading]:
    """P-16 above P-15 by a gap of `top_ratio` standard errors; P-15, P-14 and the coin a resolved ladder below."""
    sd = 0.05
    a = top_ratio * sd / math.sqrt(J)
    return _planted({"p16": 0.6 + a + sd * _standard(seed, J), "p15": np.full(J, 0.6), "p14": np.full(J, 0.45),
                     "naive_coin": np.full(J, 0.3)}, J=J)


def test_the_minimum_seed_count_holds_a_false_resolution_at_z_2_to_005() -> None:
    """m-2, the lead's ruling: H4_MIN_SEEDS is the smallest seed count at which two equal baselines' gap, ranked so the
    larger is on top (its t ratio then |t| with nJ - 1 degrees of freedom), is called resolved at z = 2 with
    probability at most 0.05; one seed fewer exceeds it."""
    rate = lambda n: 2 * stats.t.sf(R.RESOLVE_Z, n - 1)                # noqa: E731
    assert R.RESOLVE_Z == 2.0
    assert rate(R.H4_MIN_SEEDS) <= 0.05 < rate(R.H4_MIN_SEEDS - 1)


def test_resolution_at_z_2_at_the_minimum_seed_count() -> None:
    """At H4_MIN_SEEDS seeds a top gap of 2.5 standard errors is resolved and one of 1.9 is not (z = 2)."""
    d = _run(_ladder(J0, 2.5)).values["delta_star"]
    assert d["gaps"][0]["upper"] == "p16" and 2.0 < d["gaps"][0]["gap"] / d["gaps"][0]["se"]
    assert all(g["resolved"] for g in d["gaps"]) and d["resolvable"]
    d = _run(_ladder(J0, 1.9)).values["delta_star"]
    assert not d["gaps"][0]["resolved"] and all(g["resolved"] for g in d["gaps"][1:])


def test_below_the_minimum_seed_count_no_gap_is_resolved_and_the_rule_falls_back() -> None:
    """m-2: with one seed fewer than H4_MIN_SEEDS no gap is called resolved, however large: delta* is section 5's
    fallback, the fraction of the spread, between the floor and the cap -- the bound is never relaxed."""
    J = R.H4_MIN_SEEDS - 1
    d = _run(_ladder(J, 8.0)).values["delta_star"]
    assert not d["resolvable"] and not any(g["resolved"] for g in d["gaps"])
    assert d["raw"] == pytest.approx(R.DELTA_FRACTION * d["spread"])
    assert d["value"] == pytest.approx(min(R.DELTA_MAX, max(R.DELTA_MIN, d["raw"])))
    assert "seed" in d["how"]


def test_delta_star_is_held_at_its_declared_cap() -> None:
    """m-2: every gap resolved and the smallest above DELTA_MAX: delta* is DELTA_MAX, never more."""
    J = J0
    rs = _planted({"p16": np.full(J, 1.0), "p15": np.full(J, 0.65), "p14": np.full(J, 0.33),
                   "naive_coin": np.zeros(J)})
    d = _run(rs).values["delta_star"]
    assert all(g["resolved"] for g in d["gaps"]) and d["raw"] > R.DELTA_MAX
    assert d["value"] == R.DELTA_MAX and "cap" in d["how"]


def test_the_floor_and_cap_sit_on_the_three_way_notes_illustration_grid() -> None:
    """m2-1: DELTA_MIN and DELTA_MAX are the lead's choices; for context only, they are the ends of the grid the
    three-way note illustrates its power arithmetic over (`three_way_arith.DELTA`)."""
    spec = importlib.util.spec_from_file_location("three_way_arith_w42c", ARITH)
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    assert R.DELTA_MAX == max(A.DELTA) and R.DELTA_MIN == min(A.DELTA) and R.DELTA_MIN < R.DELTA_MAX


def test_delta_star_is_translated_into_each_dimensions_units(base) -> None:
    """m-2: delta* (and the floor) as the change in one dimension alone, in its own units, through its weight."""
    _, v = base
    dims = {d["name"]: d for d in v.values["dimensions"]}
    du = v.values["delta_star"]["in_units"]
    for name, d in dims.items():
        scale = 1.0 if d["kind"] == "share" else d["hi"] - d["lo"]
        assert du[name]["delta_star"] == pytest.approx(v.values["delta_star"]["value"] * scale / d["weight"])
        assert du[name]["delta_min"] == pytest.approx(R.DELTA_MIN * scale / d["weight"])


# ------------------------------------------------------------------------------- the document and the module agree
def _table(marker: str, path: Path = DOC) -> list[list[str]]:
    text = path.read_text(encoding="utf-8")
    m = re.search(rf"<!-- {marker}:start -->(.*?)<!-- {marker}:end -->", text, re.S)
    assert m, f"the document has its {marker} table"
    rows = [ln for ln in m.group(1).strip().splitlines() if ln.startswith("|")][2:]
    return [[c.strip().strip("`") for c in r.strip("|").split("|")] for r in rows]


def test_the_documents_constants_are_the_modules() -> None:
    rows = {r[0]: r[1] for r in _table("wave42-constants")}
    assert set(rows) == set(R.CONSTANTS)
    for k, v in R.CONSTANTS.items():
        assert json.loads(rows[k]) == v, k


def test_the_documents_dimensions_weights_and_limits_are_the_modules() -> None:
    dims = _table("wave42-dimensions")
    assert [(r[0], r[2], r[3], int(r[4]), r[5]) for r in dims] == \
        [(d.name, d.measure, d.key, d.horizon, "higher" if d.direction > 0 else "lower") for d in R.DIMENSIONS]
    weights = _table("wave42-weights")
    assert [r[0] for r in weights] == [d.name for d in R.DIMENSIONS]
    assert [float(r[1]) for r in weights] == pytest.approx([1 / len(R.DIMENSIONS)] * len(R.DIMENSIONS), abs=5e-4)
    lims = _table("wave42-limits")
    assert [(r[0], r[1], r[2], r[3], int(r[4]), r[5]) for r in lims] == \
        [(x.name, x.measure, x.key, x.direction, x.horizon, x.stat) for x in R.LIMITS]
    keys = _table("wave42-h4-manifest")
    assert [r[0] for r in keys] == list(R.H4_MANIFEST_KEYS)


def test_the_search_years_are_e208s_and_the_power_target_the_gates() -> None:
    charter = (ROOT / "CHARTER.md").read_text(encoding="utf-8")
    assert f"NQ {R.SEARCH_FIRST} to {R.SEARCH_LAST} (E-208)" in charter
    assert "NQ 2024-01-02 to 2026-07-16" in charter and R.HELD_OUT_FIRST == "2024-01-02"
    from extended.family_stats import MDL_POWER
    assert R.POWER_TARGET == MDL_POWER
    assert "next 13" in (ROOT / "CLAUDE.md").read_text(encoding="utf-8") and R.K_TEST == 13


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("**", "")).strip()


def test_the_document_carries_its_held_out_read_ledger() -> None:
    """B-8, V-2: the ledger section, this rule's own entry (the held-out calendar's dates only), the leak clause in
    RD-04's form, the nominal level, and CHARTER 3.6 (b)'s entries that concern the four baselines."""
    t = _norm(DOC.read_text(encoding="utf-8"))
    assert "## 10. The held-out read ledger" in DOC.read_text(encoding="utf-8")
    assert "W42-R1's own entry: the held-out session calendar's dates only" in t
    assert R.HELD_OUT_CALENDAR in t and R.HELD_OUT_CALENDAR_SHA256 in t
    assert "written after these readings; no figure from them is cited as the reason for any constant" in t
    assert "printed nominal" in t
    for entry in ("Stage 2 D-626", "E-203 S-2", "Stage 2 D-554", "RD-04 (c)", "RD-05", "Q-17 and E-201", "RD-03",
                  "program U", "RD-02", "RD-01", "Q-132", "Q-16"):
        assert entry in t, entry


def test_the_document_names_the_application_and_the_guards() -> None:
    """V-1, V-3, V-4: the script, the collection result, the adapter, the calendar, the floor and the two guards."""
    t = _norm(DOC.read_text(encoding="utf-8"))
    for phrase in ("scripts/wave42_apply.py", R.COLLECTION_RESULT, "extended/h4_collect.py", "w42_readings",
                   R.SEARCH_CALENDAR, "load_search_calendar", "standard_prices", R.OUTPUT_NAME,
                   "The do-nothing journey's composite is a declared floor", "the not_paid_within_B limit",
                   "CHARTER 3.8 (c)'s long-run gate"):
        assert phrase in t, phrase


def test_the_document_states_the_pre_pin_fixes() -> None:
    """R3-1, R3-2, R3-3, n3-1, n3-3: the audit list's three items, write-once inside a checkout, the sidecar's bytes,
    the floor at both readings, the collection row pinned first, and the H7 row's wording."""
    t = _norm(DOC.read_text(encoding="utf-8"))
    for phrase in ("extended.levers_terms.standard_prices", "extended.family_stats.MDL_POWER", "git_commit", "-dirty",
                   "write-once inside a checkout", "voids both", "CRLF normalised to LF", "at the held-out verdict",
                   "at the search-year screen", "H4's collection row is pinned before W42-R1 is applied"):
        assert phrase in t, phrase
    note = _norm(NOTE.read_text(encoding="utf-8"))
    assert "each start run to 252 sessions or the block's last session, whichever comes first" in note


def test_the_three_way_notes_limit_clause_is_e230s() -> None:
    """B-7: the three-way note's 4.4 states the point-estimate form, with W42-R1's headroom, and no margin w; m2-6:
    the count of limits has its own symbol."""
    raw = NOTE.read_text(encoding="utf-8")
    sec = raw[raw.index("### 4.4"):raw.index("## 5. The fixed sequence")]
    t = _norm(sec)
    assert "M-hat + w <= L" not in t and "(c_L + z_pi)" not in t and "w is the coin-seed half-width" not in t
    assert "the point estimate governs" in t.lower() and "E-230" in t and "W42-R1" in t
    assert "never as a second margin" in t
    assert "/ L over the L limits" not in t and "n_L" in t
    m5 = _norm(raw[raw.index("### 2.2"):raw.index("### 2.3")])
    assert "No bound is ever estimated from data, on any years." not in m5
    assert "a declared clip under (ii) may take its endpoints from the search years" in m5


def test_the_module_reads_no_file_and_imports_no_engine() -> None:
    tree = ast.parse((ROOT / "extended" / "wave42.py").read_text(encoding="utf-8"))
    mods = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    mods |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert mods <= {"__future__", "hashlib", "json", "math", "re", "dataclasses", "typing", "numpy", "scipy",
                    "extended.family_stats"}, mods
    calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "open" not in calls
    assert "random" not in (ROOT / "extended" / "wave42.py").read_text(encoding="utf-8").replace(
        "draws randomness", "")


# --------------------------------------------------------------- the public scoring path (the survey's; C-1)
PUBLIC = ("unit_values", "unit_scores", "composite_per_seed", "null_composites", "null_journeys", "limit_estimate",
          "limit_per_seed_sd", "limit_check")


def test_setting_rule_scores_through_the_public_functions(base, monkeypatch) -> None:
    """C-1: `setting_rule` calls each public function (each wrapped to count, passing through) and its output is
    unchanged by the wrapping."""
    rs, v = base
    calls = {k: 0 for k in PUBLIC}
    for name in PUBLIC:
        f = getattr(R, name)

        def wrapped(*a, _f=f, _n=name, **k):
            calls[_n] += 1
            return _f(*a, **k)
        monkeypatch.setattr(R, name, wrapped)
    again = _run(rs)
    assert again.digest() == v.digest()
    assert all(c > 0 for c in calls.values()), calls


@pytest.mark.parametrize("name,where", [
    ("composite_per_seed", lambda v: v["composite"]["value"]),
    ("unit_scores", lambda v: [d["baseline_means"] for d in v["dimensions"]]),
    ("null_composites", lambda v: v["null_journeys"]["floor"]["value"]),
    ("limit_estimate", lambda v: [x["baseline_values"] for x in v["limits"]["values"]]),
    ("limit_check", lambda v: [x["baseline_checks"] for x in v["limits"]["values"]]),
])
def test_a_change_to_a_public_function_shows_in_the_rules_output(base, monkeypatch, name, where) -> None:
    """C-1: one code path: a public function changed changes `setting_rule`'s own output where it is used."""
    rs, v = base
    f = getattr(R, name)

    def shifted(*a, **k):
        out = f(*a, **k)
        if isinstance(out, np.ndarray):
            return out + 0.01
        if name == "unit_scores":
            return {d: np.clip(z + 0.01, 0, 1) for d, z in out.items()}
        if name == "null_composites":
            return {j: c + 0.01 for j, c in out.items()}
        if name == "limit_estimate":
            return out + 0.5
        return {**out, "inside": not out["inside"]}
    monkeypatch.setattr(R, name, shifted)
    assert where(_run(rs).values) != where(v.values)


def test_the_public_functions_reproduce_the_rules_values(base) -> None:
    """The survey's view (its signatures, wt/wt-survey d5fe8f0): from the output alone, `composite_per_seed` gives each
    baseline's composite, `limit_estimate` each limit's baseline values, `do_nothing_floor` and
    `null_journeys(fee)["do_nothing"]` through `composite_per_seed` the floor, `limit_check` the checks."""
    rs, v = base
    V = json.loads(v.as_json())
    P = R.pinned_inputs(V)
    sl = _sl()
    for b in R.BASELINES:
        c = R.composite_per_seed(V, sl, rs[b].values)
        assert float(c.mean()) == pytest.approx(v.values["composite"]["value"][b], abs=1e-12)
    for L in R.LIMITS:
        got = P["limits"][L.name]
        for b in R.BASELINES:
            e = R.limit_estimate(V, sl, rs[b].values, L.name)
            assert isinstance(e, float) and e == pytest.approx(got["baseline_values"][b])
            assert R.limit_check(V, sl, rs[b].values, L.name, got["value"]) == got["baseline_checks"][b]
    assert R.do_nothing_floor(V, FEE) == pytest.approx(P["floor"])
    arm = {k: np.zeros((1, 1)) for k in R.REQUIRED}                 # the survey's own self-check, as it calls it
    arm.update({k: np.asarray([[float(x)]]) for k, x in R.null_journeys(FEE)["do_nothing"].items()})
    got = float(np.asarray(R.composite_per_seed(V, [max(R.HORIZONS)], arm)).ravel()[0])
    assert got == pytest.approx(V["null_journeys"]["floor"]["value"], abs=1e-12)
    assert P["form"] == v.values["form"] and P["floor"] == v.values["null_journeys"]["floor"]["value"]


def test_a_design_that_never_passes_scores_zero_on_cost_through_the_public_path(base) -> None:
    """B-5 through `unit_scores`: a design set with no unit passed by W, however little it spends, has cost z = 0 on
    every unit, so its composite carries no cost credit (the survey's C-1 defect)."""
    rs, v = base
    V = json.loads(v.as_json())
    P = R.pinned_inputs(V)
    d = {k: np.asarray(x, dtype=float).copy() for k, x in rs["p14"].values.items()}
    d["first_pass_days"] = np.where(np.isnan(d["first_pass_days"]), np.nan, R.W + 1.0)
    d["first_payout_days"] = np.where(np.isnan(d["first_payout_days"]), np.nan, R.W + 1.0)
    d["cash_to_first_pass"] = np.where(np.isnan(d["cash_to_first_pass"]), np.nan, 0.0)
    z = R.unit_scores(d, P["B"], P["caps"])
    assert np.all(z["cost"][_sl() >= R.W] == 0.0)
    no_cost = {**V, "weights": {k: w for k, w in V["weights"].items() if k != "cost"}}
    assert R.composite_per_seed(V, _sl(), d) == pytest.approx(R.composite_per_seed(no_cost, _sl(), d))


def test_limit_check_decides_by_the_point_estimate_and_reports_the_crossing_beside() -> None:
    """E-230: inside decides (a ceiling at or below its value); the one-sided check of crossing at LIMIT_CHECK_LEVEL is
    beside -- an estimate just above the value is outside but not shown crossed; one far above is both."""
    L = next(x for x in R.LIMITS if x.name == "first_payout_days_p50")
    sl = np.full(10, 300)
    rng = np.random.default_rng(3)
    x = np.full((10, 40), 50.0) + rng.normal(0, 1.0, (10, 40))
    vals = {"first_payout_days": x, "spent_before_first_payout": np.zeros((10, 40)),
            **{f"net_month_{m}": np.zeros((10, 40)) for m in (1, 2, 3)},
            **{f"peak_month_{m}": np.zeros((10, 40)) for m in (1, 2, 3)}}
    V = {"budgets": {"primary": 100.0}}
    e = R.limit_estimate(V, sl, vals, L.name)
    assert e == pytest.approx(float(np.quantile(x, 0.5)))                 # the pooled point estimate
    assert R.limit_check(V, sl, vals, L.name, e)["inside"]                # at the value is inside
    assert R.limit_check(V, sl, vals, L.name, e + 1e-9)["inside"]
    near = R.limit_check(V, sl, vals, L.name, e - 1e-6)
    assert not near["inside"] and not near["crossed_at_level"]
    far = R.limit_check(V, sl, vals, L.name, e - 5.0)
    assert not far["inside"] and far["crossed_at_level"]
    F = next(x for x in R.LIMITS if x.direction == "floor")              # a floor, the mirror image
    fv = {**vals, F.key: x}
    ef = R.limit_estimate(V, sl, fv, F.name)
    assert R.limit_check(V, sl, fv, F.name, ef - 1.0)["inside"]
    below = R.limit_check(V, sl, fv, F.name, ef + 5.0)
    assert not below["inside"] and below["crossed_at_level"] and below["beyond"] == pytest.approx(5.0)


def test_the_documents_output_row_schema_is_the_outputs(base) -> None:
    """The row schema of `w42_r1_values.csv` (section 9): one row per top-level key of the values, `key` and
    `value_json`; the document's table lists exactly those keys."""
    _, v = base
    rows = _table("wave42-output-rows")
    assert [r[0] for r in rows] == sorted(v.values)


def test_the_public_signatures_are_the_surveys() -> None:
    """The survey (wt/wt-survey d5fe8f0) binds to these exact signatures."""
    sig = lambda f: list(inspect.signature(f).parameters)                 # noqa: E731
    assert sig(R.composite_per_seed) == ["values", "sessions_left", "out"]
    assert sig(R.limit_estimate) == ["values", "sessions_left", "out", "name"]
    assert sig(R.null_journeys) == ["fee_unit"] and "do_nothing" in R.null_journeys(1.0)
    assert sig(R.limit_check) == ["values", "sessions_left", "out", "name", "value", "level_"]
