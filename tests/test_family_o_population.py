"""F-03 (family O, `prereg/F-03_opening_timing.md`) T-4, T-6, T-16, T-17 and T-14: the population and its strata, the
estimand on the family's own code, K0, the clustered twin and the stage-B pick (sections 5.2, 7, 9 A11, 10; build items
18.1 items 2 and 5). Synthetic inputs only; seeds `[SEED_TESTS, ...]` (section 16's test block) and the declared
generators where the code under test draws (`[SEED_TWIN, c, b, d]`, `[SEED_K0, cell, form, j]`).
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from extended import features as F
from extended import lift_bound as LB
from extended import opening_population as OP
from extended import opening_run as RUN
from extended import opening_stats as ST
from extended import walker as Wk

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261988
MARKS = list(range(0, F.slot(9, 0) + 1, 5))                    # P-16's marks 17:00 .. 09:00 (synthetic admitted set)
RR = (1.0, 1.5, 2.0, 3.0)
COSTS = Wk.Costs(1.37, 0.5, 1.0)


def synthetic_day(rng, step: int):
    """One trading day's walker arrays, indexed by bar end (1 .. 1330), a +-step random walk on the 0.25 grid."""
    n = 1331
    o, h, l, c = (np.full(n, np.nan) for _ in range(4))
    last = 20000.0
    for j in range(1, n):
        o[j] = last
        c[j] = o[j] + 0.25 * step * rng.integers(-1, 2)
        h[j] = max(o[j], c[j]) + 0.25 * rng.integers(0, 3)
        l[j] = min(o[j], c[j]) - 0.25 * rng.integers(0, 3)
        last = c[j]
    return o, h, l, c


@pytest.fixture(scope="module")
def walked():
    days = ["2021-03-01", "2021-03-02", "2021-03-03", "2021-03-04", "2021-03-05", "2022-03-01"]
    kinds = {"2021-03-01": "n", "2021-03-02": "b", "2021-03-03": "n", "2021-03-04": "f", "2021-03-05": "n",
             "2022-03-01": "b"}
    arr = {d: synthetic_day(np.random.default_rng([SEED, 600, i]), 2 + i % 3) for i, d in enumerate(days)}
    walk_days = [d for d in days if kinds[d] in ("n", "b")]
    mins = pd.DataFrame([(d, m) for d in walk_days for m in MARKS], columns=["date", "slot"])
    w = OP.walk_offers(mins, lambda d: arr[d], RR, rules=Wk.STAGE2)
    wc = OP.walk_offers(mins, lambda d: arr[d], [3.0], rules=OP.CLOSE_RULES)
    coins = {(d, m): (1 if (i + m // 5) % 2 else -1) for i, d in enumerate(days) for m in MARKS}
    pop = OP.population_frame(w, wc, coins, kinds, MARKS, rr_grid=RR, costs=COSTS, entry_ticks=1.0)
    return {"days": days, "kinds": kinds, "arr": arr, "mins": mins, "walk": w, "close": wc, "pop": pop}


# ------------------------------------------------------------------------------------------------ T-4


def test_t4_the_walk_is_e011s_walk_under_stage2(walked):
    sys.path.insert(0, str(ROOT / "identity"))
    try:
        import walker_identity as WI
    finally:
        sys.path.remove(str(ROOT / "identity"))
    theirs = WI.walk_minutes(walked["mins"], lambda d: walked["arr"][d], 0, Wk.TICK, (150,), RR)
    pd.testing.assert_frame_equal(walked["walk"], theirs, check_exact=True)


def test_t4_the_population_is_p16s_overnight_marks_report_days_from_0740(walked):
    pop = walked["pop"]
    p = pop[pop["population"]]
    lab = pop[pop["label"]]
    assert set(pop["day_kind"]) == {"n", "b"}                     # never an FOMC day, an early close or an empty day
    assert p["slot"].between(0, F.slot(8, 25)).all()
    assert not p["slot"].between(F.slot(8, 30), F.slot(9, 0)).any()
    assert (p.loc[p["day_kind"] == "b", "slot"] >= F.slot(7, 40)).all()
    assert (p.loc[p["day_kind"] == "n", "slot"].min()) == 0
    # the labels: every other P-16 offer -- the 08:30-09:00 marks and the report-day 07:35 mark
    assert set(lab.loc[lab["day_kind"] == "n", "slot"]) <= set(range(F.slot(8, 30), F.slot(9, 0) + 1, 5))
    assert set(lab.loc[lab["day_kind"] == "b", "slot"]) <= {F.slot(7, 35), *range(F.slot(8, 30), F.slot(9, 0) + 1, 5)}
    assert F.slot(7, 35) in set(lab.loc[lab["day_kind"] == "b", "slot"])
    # a report day's marks before 07:35 are not P-16's (D-533 (2)): in neither
    assert not ((pop["day_kind"] == "b") & (pop["slot"] < F.slot(7, 35))).any()
    assert not (pop["population"] & pop["label"]).any()


def test_t4_the_values_are_stage2s_net_r_and_c_the_side_symmetric_mean(walked):
    pop, w = walked["pop"], walked["walk"]
    r = pop.iloc[7]
    lo = w[(w["date"] == r["date"]) & (w["slot"] == r["slot"]) & (w["side"] == 1)].iloc[0]
    want = Wk.net_r(np.array([lo["g150_3"]]), np.array([lo["k150_3"]]), 150, entry_ticks=1.0, costs=COSTS)[0]
    assert r["rl"] == want and r["rl_3"] == want
    assert np.allclose(pop["c"], (pop["rl"] + pop["rs"]) / 2.0)
    flat = (pop["kl"] == Wk.FLATTEN)
    assert np.array_equal(pop.loc[~flat, "rl"], pop.loc[~flat, "rl_close"])
    assert (pop.loc[flat, "rl_close"] > pop.loc[flat, "rl"]).all()
    assert flat.any()


def test_t4_the_strata_are_mark_day_kind_and_year_and_centring_zeroes_them(walked):
    pop = OP.centre(walked["pop"])
    assert pop["g"].iloc[0] == f"{pop['slot'].iloc[0]}|{pop['day_kind'].iloc[0]}|{pop['year'].iloc[0]}"
    assert np.allclose(pop.groupby("g")["y"].sum(), 0.0, atol=1e-12)
    both = pop.groupby("g")[["population", "label"]].agg(lambda x: x.any())
    assert not (both["population"] & both["label"]).any()          # a stratum is wholly population or labels


def test_t4_the_coin_and_the_session_list():
    dates = ["2020-01-02", "2020-01-03", "2024-01-02"]
    slots = list(range(0, 1330, 5))
    ca = OP.CoinArray(dates, slots, 20261102)
    u = np.random.default_rng(20261102).random(len(dates) * len(slots))
    side = np.where(u < 0.5, 1, -1)
    assert all(ca[(d, s)] == side[i * len(slots) + j] for i, d in enumerate(dates) for j, s in enumerate(slots))
    cal = [str(d.date()) for d in pd.bdate_range("2024-01-02", periods=OP.JUDGED_SESSIONS_COUNT)]
    with pytest.raises(ValueError, match="REFUSED"):
        OP.judged_sessions(cal)                                    # 657 sessions, but not E-094's list
    with pytest.raises(ValueError, match="REFUSED"):
        OP.judged_sessions(cal[:-1])
    assert np.array_equal(OP.session_ordinals(["2024-01-03", "2024-01-02"], cal), [1, 0])


# ------------------------------------------------------------------------------------------------ a synthetic block


def block(rng, n: int = 300, marks=(0, 30, 60, 300, 600, 880, 925), share: float = 1 / 3, run: float = 8.0,
          years=(2021, 2022, 2023)):
    sessions = [str(d.date()) for d in pd.bdate_range("2021-01-04", periods=n)]
    year = np.array([int(s[:4]) for s in sessions])
    kinds = np.where(rng.random(n) < 0.15, "b", "n")
    rows = []
    for i, s in enumerate(sessions):
        for m in marks:
            if kinds[i] == "b" and m < F.slot(7, 40):
                continue
            rows.append((s, int(m), kinds[i], int(s[:4])))
    pop = pd.DataFrame(rows, columns=["date", "slot", "day_kind", "year"])
    pop["population"] = True
    reg = np.where(rng.random(n) < 0.5, 0.2, -0.2)
    eff = pd.Series(reg, index=sessions)
    pop["rl"] = rng.normal(size=len(pop)) + eff.loc[pop["date"]].to_numpy() + 0.3 * (pop["year"] - 2022)
    pop["rs"] = rng.normal(size=len(pop)) - eff.loc[pop["date"]].to_numpy() + 0.3 * (pop["year"] - 2022)
    pop["c"] = (pop["rl"] + pop["rs"]) / 2.0
    stay = 1 - 1 / run
    enter = (1 / run) * share / (1 - share)
    st = np.zeros(n, bool)
    u = rng.random(n)
    for t in range(1, n):
        st[t] = (u[t] < stay) if st[t - 1] else (u[t] < enter)
    pop["state"] = pd.Series(st, index=sessions).loc[pop["date"]].to_numpy()
    return pop, sessions


# ------------------------------------------------------------------------------------------------ T-6


def test_t6_the_lift_is_the_exact_twin_and_placebo_selection_bounds_estimate():
    rng = np.random.default_rng([SEED, 610])
    pop, sessions = block(rng)
    L = ST.layout(pop, sessions, values=("c", "rl", "rs"), flags=("state",))
    y = ST.centred(L, "c")
    sel = L.flags["state"]
    lift = ST.lift(L, y, sel)
    line = ST.c1_line(L, y, sel, RUN.LEVEL)
    assert abs(line.nominal.estimate - lift) < 1e-12
    assert all(abs(m.estimate - lift) < 1e-12 for m in line.members)
    # the exact twin is the drawn twins' mean: random filters firing on each stratum's count, without replacement
    draws = []
    for d in range(400):
        r = np.random.default_rng([SEED, 611, d])
        tw = np.zeros_like(sel)
        for g in range(len(L.groups)):
            rows = np.flatnonzero(L.group == g)
            for k in range(len(L.marks)):
                cand = rows[L.population[rows, k]]
                kk = int(sel[cand, k].sum())
                if kk:
                    tw[r.choice(cand, kk, replace=False), k] = True
        draws.append(np.nanmean(np.where(tw, L.values["c"], np.nan)[tw]))
    exact = float(np.nansum(np.where(sel, L.values["c"] - y, 0.0)) / sel.sum())   # the in-state offers' mean mu_g
    assert abs(np.mean(draws) - exact) < 4 * np.std(draws) / np.sqrt(len(draws))
    assert abs((np.nanmean(L.values["c"][sel]) - exact) - lift) < 1e-12


def test_t6_an_uninformative_state_averages_no_lift_and_the_halves_average_to_l():
    lifts = []
    for k in range(60):
        rng = np.random.default_rng([SEED, 620, k])
        pop, sessions = block(rng, n=120)
        pop["state"] = rng.random(len(pop)) < 1 / 3
        L = ST.layout(pop, sessions, values=("c", "rl", "rs"), flags=("state",))
        y = ST.centred(L, "c")
        lifts.append(ST.lift(L, y, L.flags["state"]))
        h = ST.halves(L, L.flags["state"])
        assert abs(h["mean"] - lifts[-1]) < 1e-12
    assert abs(np.mean(lifts)) < 3 * np.std(lifts) / np.sqrt(len(lifts))


def test_t6_d_and_v_line_are_their_hand_sums_and_a_fallback_takes_its_label():
    y1 = np.array([0.5, -0.25, 1.0])            # the design's openings' centred values
    s1 = np.array([0, 3, 3])
    y2 = np.array([0.0, 0.25, -0.5, 0.75])      # the twin designs' (two draws pooled)
    s2 = np.array([1, 2, 3, 4])
    D, _ = ST.d_bootstrap_se(y1, s1, y2, s2, 63, draws=50)
    assert abs(D - (y1.mean() - y2.mean())) < 1e-15
    assert ST.v_line(2.0, 1200.0, D) == 2.0 * 1200.0 * D / 4.0
    assert abs(ST.openings_a_start_year(30, [252, 126]) - 30 / 1.5) < 1e-12
    # a fallback opening at a labelled mark takes its label's centred value (its own stratum)
    lab = pd.DataFrame({"date": ["2021-01-04", "2021-01-05"], "slot": [F.slot(8, 45)] * 2, "day_kind": ["n", "n"],
                        "year": [2021, 2021], "c": [0.4, -0.2], "population": [False, False], "label": [True, True]})
    c = OP.centre(lab)
    assert np.allclose(c["y"], [0.3, -0.3])


# ------------------------------------------------------------------------------------------------ T-17


def test_t17_the_clustered_twin_keeps_counts_and_runs_and_its_frequency_is_the_share():
    rng = np.random.default_rng([SEED, 630])
    pop, sessions = block(rng, n=260, run=12.0)
    L = ST.layout(pop, sessions, values=("c",), flags=("state",))
    st = L.flags["state"]
    tw, offs = ST.clustered_twin(L, st, cell=0, block=ST.BLOCK_CHOICE, draw=0)
    for g in range(len(L.groups)):
        rows = L.group == g
        assert np.array_equal(tw[rows].sum(axis=0), st[rows].sum(axis=0))          # every stratum's count
    # the runs survive except at the wrap: within a sequence the twin is the state read at a shifted session
    seq = np.flatnonzero((L.kind == "n") & (L.year == 2021))
    k = offs[("n", 2021)]
    assert np.array_equal(tw[seq], st[seq[(np.arange(len(seq)) + k) % len(seq)]])
    # over many offsets each offer's frequency is its stratum's share
    freq = np.zeros(st.shape)
    R = 3000
    for d in range(R):
        freq += ST.clustered_twin(L, st, 1, ST.BLOCK_CHOICE, 1000 + d)[0]
    for g in range(len(L.groups))[:3]:
        rows = np.flatnonzero(L.group == g)
        share = st[rows].mean(axis=0)
        assert np.allclose(freq[rows] / R, share[None, :], atol=0.06)


# ------------------------------------------------------------------------------------------------ T-16


def test_t16_k0_on_the_familys_code_is_the_toys_machinery_and_its_verdict_the_interval():
    sys.path.insert(0, str(ROOT / "tests"))
    import test_family_o_toys as TOY

    rng = np.random.default_rng([SEED, 640])
    nc, nj, reps = 750, 630, 400
    N1s = rng.binomial(186, 1 / 3, nc)
    N2s = np.full(nc, 186)
    toy = TOY.k0_rejections(N1s, N2s, "nested", reps, [SEED, 641], chunk=reps)
    # the same draws, in the toy's order, through the family's statistic
    r = np.random.default_rng([SEED, 641])
    t = np.arange(nj)
    idx = (r.integers(0, nc, reps)[None, :] + t[:, None]) % nc
    N1, N2 = N1s[idx], N2s[idx]
    p = ST.stats.norm.cdf(r.standard_normal((nj, reps)) * np.sqrt(ST.K0_ICC) / np.sqrt(1 - ST.K0_ICC))
    u1 = r.binomial(N1, p)
    ur = r.binomial(N2 - N1, p)
    S1 = 0.5 * (2 * u1 - N1)
    S2 = S1 + 0.5 * (2 * ur - (N2 - N1))
    for i, a in enumerate(TOY.LEVELS):
        assert ST.k0_rejections_from_sums(S1, N1.astype(float), S2, N2.astype(float), a) == toy[i]
    v = ST.k0(N1s, N2s, "nested", nj, TOY.LEVELS[0], lambda j: ST.rng_of(SEED, 642, j), replications=300)
    lo, hi = LB.clopper_pearson(v.rejections, v.replications)
    assert (v.ci_lo, v.ci_hi) == (lo, hi) and v.lax == (lo > TOY.LEVELS[0])


def test_t16_k0_reads_no_value_and_draws_by_its_declared_generator():
    rng = np.random.default_rng([SEED, 643])
    N1s, N2s = rng.binomial(30, 0.4, 200), rng.binomial(30, 0.4, 200)
    a = ST.k0_family(N1s, N2s, "pair", 120, 0.05, cell=0, form_index=1, replications=200)
    b = ST.k0_family(N1s, N2s, "pair", 120, 0.05, cell=0, form_index=1, replications=200)
    assert a == b                                                   # deterministic by [SEED_K0, cell, form, j]
    import inspect
    assert "value" not in inspect.signature(ST.k0).parameters and "y" not in inspect.signature(ST.k0).parameters
    assert ST.SEED_K0 == 20261989 and ST.K0_REPLICATIONS == 200_000


# ------------------------------------------------------------------------------------------------ T-14


def test_t14_the_pick_is_a_function_of_the_choice_section_alone(tmp_path):
    cells = ["s1", "s2", "u3"]
    est, se = {"s1": 0.04, "s2": 0.05, "u3": 0.01}, {"s1": 0.01, "s2": 0.01, "u3": 0.01}
    elig = {"s1": True, "s2": True, "u3": True}
    vlow = {"s1": 120.0, "s2": 80.0, "u3": 300.0}
    p = ST.stage_b_pick(cells, est, se, 2.5, elig, vlow)
    assert p["pick"] == "s1" and not p["killed"]                   # u3 is not above q_B
    rows = [{"section": "choice", "kind": "cell", "cell": c, "L": est[c], "SE": se[c], "eligible": elig[c],
             "V_B_lower": vlow[c]} for c in cells]
    rows.append({"section": "choice", "kind": "q_B", "value": 2.5})
    rows.append({"section": "choice", "kind": "pick", "cell": p["pick"], "killed": p["killed"]})
    f = tmp_path / "choice.csv"
    RUN.frame(rows, RUN.RUN1_SECTIONS).to_csv(f, index=False)
    back = pd.read_csv(f)
    c = back[back["kind"] == "cell"].set_index("cell")
    q = float(back.loc[back["kind"] == "q_B", "value"].iloc[0])
    again = ST.stage_b_pick(cells, c["L"].to_dict(), c["SE"].to_dict(), q, c["eligible"].astype(bool).to_dict(),
                            c["V_B_lower"].to_dict())
    assert again["pick"] == RUN.choice_pick(back)["pick"] == p["pick"]
    tie = ST.stage_b_pick(cells, est, se, 2.5, elig, {"s1": 80.0, "s2": 80.0, "u3": 0.0})
    assert tie["pick"] == "s1"                                     # ties to the cell listed first
    assert ST.stage_b_pick(cells, est, se, 9.0, elig, vlow) == {"killed": True, "pick": None, "above": []}


# ------------------------------------------------------------------------------------------------ the larger-of rule and B2


def test_the_larger_of_rule_takes_the_larger_critical_value_per_member():
    rng = np.random.default_rng([SEED, 650])
    pop, sessions = block(rng, n=300)
    L = ST.layout(pop, sessions, values=("c",), flags=("state",))
    y = ST.centred(L, "c")
    nom = ST.c1_line(L, y, L.flags["state"], 0.05)
    big = ST.c1_line(L, y, L.flags["state"], 0.05, b2={21: 50.0, 42: 50.0, 63: 50.0})
    for a, b in zip(nom.members, big.members):
        assert b.crit == 50.0 and a.crit == a.t_crit and b.lower < a.lower
    assert not big.passes
    assert abs(nom.bound - min(m.lower for m in nom.members)) < 1e-15


def test_b2_replicates_are_centred_in_the_judged_strata_and_seeded_per_replicate():
    rng = np.random.default_rng([SEED, 660])
    pop, sessions = block(rng, n=260)
    Lc = ST.layout(pop, sessions, values=("c",), flags=("state",))
    yc = ST.centred(Lc, "c")
    popj, sj = block(np.random.default_rng([SEED, 661]), n=130)
    Lj = ST.layout(popj, sj, values=("c",), flags=("state",))
    inp = ST.B2Inputs(yc, Lc.kind, Lj.kind, Lj.group, Lj.exists, (Lj.flags["state"] & Lj.population).astype(float),
                      Lj.population.astype(float))
    S1, N1, S2, N2 = ST.b2_replicate_sums(inp, 0.5, ST.rng_of(ST.SEED_B2, 0, 7))
    assert abs(S2.sum()) < 1e-9                                     # re-centred within the judged strata
    q1, T1 = ST.b2_quantiles(inp, 0.0, 0.05, ST.LINE_C1, replicates=60, keep=True, chunk=17)
    q2, T2 = ST.b2_quantiles(inp, 0.0, 0.05, ST.LINE_C1, replicates=60, keep=True, chunk=60)
    assert np.array_equal(T1, T2, equal_nan=True) and q1 == q2      # the chunking changes no draw
    assert np.isfinite(T1).mean() > 0.9


def test_a_star_parts_take_no_in_state_offer():
    rng = np.random.default_rng([SEED, 670])
    pop, sessions = block(rng, n=200)
    L = ST.layout(pop, sessions, values=("c",), flags=("state",))
    out = ~L.flags["state"] & L.population
    d0 = ST.amplitude_d(L, "c", out)
    V = L.values["c"].copy()
    V[L.flags["state"]] += 100.0                                     # a huge lift in state
    L.values["c"] = V
    assert ST.amplitude_d(L, "c", out) == d0
    assert ST.block_mean_amplitude(np.r_[np.ones(63), -2 * np.ones(63), np.zeros(10)]) == pytest.approx(
        max(abs(np.r_[np.ones(63), -2 * np.ones(63), np.zeros(10)][(LB.block_index(136, 63)[0] == g)].mean())
            for g in range(2)))


def test_a10_flags_lax_by_the_interval_and_draws_by_its_declared_generator():
    rng = np.random.default_rng([SEED, 680])
    pop, sessions = block(rng, n=120, marks=(0, 300, 600))
    L = ST.layout(pop, sessions, values=("c",), flags=("state",))
    y = ST.centred(L, "c")
    t = ST.a10(L, y, classes=("session", "window"), shares=(0.25,), selections=40)
    assert set(t.columns) >= {"class", "share", "level", "rejections", "ci_lo", "ci_hi", "lax"}
    assert all(r.lax == (r.ci_lo > r.level) for r in t.itertuples())
    t2 = ST.a10(L, y, classes=("session", "window"), shares=(0.25,), selections=40)
    pd.testing.assert_frame_equal(t, t2)


def test_the_kills_read_as_declared():
    assert ST.k1_killed({2021: 30, 2022: 20, 2023: 40}) and not ST.k1_killed({2021: 21, 2022: 21, 2023: 21})
    assert ST.k2_killed({"overall": 0.03, "2021": 0.06, "2022": 0.0, "2023": 0.0})
    assert not ST.k2_killed({"overall": 0.05, "2021": 0.05, "2022": 0.0, "2023": 0.01})
    assert ST.k5_killed(0.51) and not ST.k5_killed(0.5)
    assert ST.lambda_bar(1000.0, 2.0) == 1.0
