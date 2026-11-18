"""F-03 (family O, `prereg/F-03_opening_timing.md`) A10's consequence (9; the build read's M1; the lead's reading in
E-112: the inner draws keyed by A10's replication key extended by the inner index), the refusals of non-finite values
(m6), A9 within day kind (m2), A3's further checks on a frame (M3) and the judge that never refits (M5). Toy inputs.
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import opening_states as OS
from extended import opening_stats as ST
from extended import synthetic_bars as sb


def toy(seed: int, n_years=(2021, 2022, 2023), per_year: int = 130, marks=(0, 300, 600), slow: float = 0.0):
    rng = np.random.default_rng([ST.SEED_TESTS, 900, seed])
    sessions = []
    for y in n_years:
        sessions += [str(d.date()) for d in pd.bdate_range(f"{y}-01-04", periods=per_year)]
    kinds = np.where(rng.random(len(sessions)) < 0.15, "b", "n")
    sign = ST.slow_sign(rng, len(sessions), 1 / 21)
    rows = []
    for i, s in enumerate(sessions):
        common = slow * sign[i] + rng.normal(0, 0.3)
        for m in marks:
            rows.append((s, m, kinds[i], int(s[:4]), True, common + rng.normal(0, 0.8)))
    pop = pd.DataFrame(rows, columns=["date", "slot", "day_kind", "year", "population", "c"])
    return ST.layout(pop, sessions, values=("c",))


@pytest.mark.parametrize("model", ["session", "window"])
def test_the_shortcut_is_the_naive_computation_exactly(model):
    L = toy(1, slow=0.8)
    a = ST.a10_consequence(L, "c", model, 0.0, shares=(0.5,), selections=12, inner=60, shortcut=True)
    b = ST.a10_consequence(L, "c", model, 0.0, shares=(0.5,), selections=12, inner=60, shortcut=False)
    assert a.decisions == b.decisions
    assert [r["rejections"] for r in a.rows] == [r["rejections"] for r in b.rows]
    assert a.b2_runs <= b.b2_runs == 12


def test_a_selections_answer_does_not_depend_on_which_others_are_skipped_or_run():
    L = toy(2, slow=0.8)
    small = ST.a10_consequence(L, "c", "block5", 0.0, shares=(0.25,), selections=6, inner=40)
    large = ST.a10_consequence(L, "c", "block5", 0.0, shares=(0.25,), selections=12, inner=40)
    for k, v in small.decisions.items():
        assert large.decisions[k][:6] == v


def test_the_consequence_closes_on_an_interval_wholly_above_and_keeps_otherwise(monkeypatch):
    L = toy(3)
    real = ST.larger_of

    def always(S1, N1, S2, N2, level, b2=None, nominal=None):
        line = real(S1, N1, S2, N2, level, b2, nominal)
        line.passes = True
        return line

    monkeypatch.setattr(ST, "larger_of", always)
    r = ST.a10_consequence(L, "c", "session", 0.0, shares=(0.25,), selections=20, inner=30)
    assert r.closed and all(x["lax"] for x in r.rows)
    monkeypatch.setattr(ST, "larger_of", real)
    r = ST.a10_consequence(L, "c", "session", 0.0, shares=(0.25,), selections=20, inner=30)
    assert all(x["lax"] == (x["ci_lo"] > x["level"]) for x in r.rows)
    assert r.closed == any(x["lax"] for x in r.rows)


def test_the_consequence_keys_its_inner_draws_by_a10s_key_and_the_inner_index():
    L = toy(4, slow=0.8)
    a = ST.a10_consequence(L, "c", "session", 0.0, shares=(0.5,), selections=8, inner=40)
    b = ST.a10_consequence(L, "c", "session", 0.0, shares=(0.5,), selections=8, inner=40)
    assert a.decisions == b.decisions and a.rows == b.rows


def test_non_finite_values_are_refused_never_a_fall_back():
    L = toy(5)
    y = ST.centred(L, "c", L.population)
    with pytest.raises(ST.NotFinite):
        ST.c1_line(L, y, L.population, 0.05, b2={21: np.nan, 42: 1.0, 63: 1.0})
    bad = ST.B2Inputs(np.full_like(y, np.nan), L.kind, L.kind, L.group, L.exists, L.population.astype(float),
                      L.population.astype(float))
    with pytest.raises(ST.NotFinite):
        ST.b2_quantiles(bad, 0.0, 0.05, 0, replicates=3)
    with pytest.raises(ST.NotFinite):
        ST.stage_b_pick(["s1"], {"s1": 1.0}, {"s1": 0.0}, 1.0, {"s1": True}, {"s1": 10.0})


def test_a9_aligns_within_day_kind_from_63_sessions_on():
    L = toy(6, per_year=120)
    idx = ST.within_kind_index(L, np.arange(L.n), 70)
    assert (L.kind[idx] == L.kind).all() and (idx != np.arange(L.n)).all()
    y = ST.centred(L, "c", L.population)
    sel = L.population & (np.random.default_rng([ST.SEED_TESTS, 901]).random(L.population.shape) < 0.3)
    m = ST.a9_mdl(L, y, sel, 200, 0.05)
    assert m["offsets"] == [63, L.n - 64] and m["windows"] == L.n - 126 and np.isfinite(m["mdl"])


@pytest.fixture(scope="module")
def frame():
    g = F.grid(sb.generate(sb.Spec(date(2020, 6, 1), date(2021, 2, 26), seed=[ST.SEED_TESTS, 902],
                                   holidays=frozenset(), early_closes=frozenset())))
    return g, OS.compute(g)


def test_a3s_window_and_degenerate_checks_on_a_frame(frame):
    g, st = frame
    defined = [i for i in range(len(st.days)) if np.isfinite(st.share("s1")[i]).any()]
    assert OS.window_problems(g, st, defined[:3], ST.SEED_SHIFT) == []
    assert OS.degenerate_problems(st) == []
    broken = OS.States(st.days, st.marks, {**st.shares, "u3": np.full_like(st.shares["u3"], np.nan)}, st.forecast)
    assert any("u3 is undefined everywhere" in p for p in OS.degenerate_problems(broken))


def test_the_judge_never_refits(frame):
    g, st = frame
    with pytest.raises(ValueError, match="nothing is fitted"):
        OS.compute(g, frozen=st.forecast.final)
    again = OS.compute(g, frozen=st.forecast.final, test_years=())
    assert again.forecast.folds == {} and again.forecast.final == st.forecast.final
