"""RD-05's T-5 and T-6 (`prereg/RD-05_firm_modes.md` 17.3): part A's arithmetic on hand-built rule sets with known
answers, under both consistency semantics; `k_F` under a calendar and a trading-day clock with 2.6's rounding; `b*` at
both U-25 ends; the implied-days, boundary-cell, close-only and ceiling-cell lists; the stated-fewest check firing on a
hand-broken record; A-19's parser on each named quote and refusing a hand-broken one. Part B on hand-computed cells,
the three mixes, U-26's two counts, the constants read from their modules. Pure arithmetic; fast.
"""
from __future__ import annotations

import math
from dataclasses import replace

import pytest

from extended import modes_rules as R
from extended import modes_terms as M
from extended.firm_terms import TermParseError


def ev(**kw) -> M.EvalTerms:
    base = M.eval_terms("TS-S")
    return replace(base, **kw)


# ------------------------------------------------------------------------------------------------- T-5, part A


@pytest.mark.parametrize("c,md,life,want", [(0.55, None, None, 2), (0.3, 4, None, 4), (0.3, None, None, 4),
                                            (0.5, 2, None, 2), (0.4, None, None, 3), (None, 1, None, 1),
                                            (0.25, None, 3, None), (0.5, 5, None, 5)])
def test_k_eval_hand_built(c, md, life, want) -> None:
    t = ev(consistency=c, min_days=md, lifespan=life)
    for sem in ("extends", "fails"):
        assert R.k_eval(t, sem) == want


def test_further_days_both_semantics() -> None:
    t = ev(target=3000.0, consistency=0.5, min_days=None)
    a = R.further_days(t, 1500.0, "extends")
    assert a["raised_target"] == 3000.0 and a["further_days"] == 1
    b = R.further_days(t, 3000.0, "extends")
    assert b["raised_target"] == 6000.0 and b["further_days"] == 1
    c = R.further_days(t, 4500.0, "extends")
    assert c["raised_target"] == 9000.0 and c["further_days"] == 1
    assert R.further_days(t, 3000.0, "fails")["survives"] is False
    assert R.further_days(t, 1500.0, "fails")["survives"] is True
    d = R.further_days(ev(target=3000.0, consistency=0.3, min_days=4), 900.0, "extends")
    assert d["further_days"] == 3                       # (3000 - 900) / 900 -> 3 more, and 4 days in all
    assert [x / 3000.0 for x in R.first_day_levels(ev(consistency=0.5))] == [0.5, 0.75, 1.0, 1.5]


def test_calendar_rounding_up_for_waits_down_for_windows() -> None:
    assert M.calendar_to_sessions(14, wait=True) == math.ceil(14 * 21 / 30)
    assert M.calendar_to_sessions(7, wait=False) == math.floor(7 * 21 / 30)
    assert M.calendar_to_sessions(90, wait=False) == 63 and M.calendar_to_sessions(30, wait=True) == 21
    assert M.calendar_to_sessions(1, wait=True) == 1 and M.calendar_to_sessions(1, wait=False) == 0


def test_k_funded_per_gate() -> None:
    assert R.k_funded(M.funded_terms("TS/std"))["k_F"] == 5
    assert R.k_funded(M.funded_terms("TS/con"))["k_F"] == 3
    pro = M.funded_terms("PRO", M.STRICT)
    assert R.k_funded(pro)["k_F"] == M.calendar_to_sessions(14, wait=True) + 1     # a calendar clock
    assert R.k_funded(M.funded_terms("RE", M.STRICT))["k_F"] == 2                   # 24 hours: one session, then 1
    assert R.k_funded(M.funded_terms("L10/day", M.STRICT))["k_F"] == 2
    assert R.k_funded(M.funded_terms("L10/day", M.LENIENT))["k_F"] == 1
    assert R.k_funded(M.funded_terms("B20", M.STRICT))["k_F"] == 3
    assert R.k_funded(M.funded_terms("LU"))["k_F"] == 5
    # a trading-day clock counts trading sessions: a hand-built gate with a wait of 3 sessions
    hb = replace(M.funded_terms("RE", M.STRICT), wait_first=3)
    assert R.k_funded(hb)["k_F"] == 4


def test_b_star_at_both_u25_ends() -> None:
    cap = R.reference_cap()
    s, l = M.funded_terms("RE", M.STRICT), M.funded_terms("RE", M.LENIENT)
    assert R.b_star(s)["b_star"] == pytest.approx(max(cap / s.frac, s.buffer + cap))
    assert R.b_star(l)["b_star"] == pytest.approx(l.buffer + cap)
    assert R.b_star(l)["label"] == "b* at the reference cap"
    pl = M.funded_terms("PRO", M.LENIENT)
    assert R.b_star(pl)["b_star"] == pytest.approx(pl.buffer + cap)          # R-d: the share only inside the buffer
    assert R.request_amount(pl, pl.buffer - 100.0) == pytest.approx(pl.within_buffer_share * (pl.buffer - 100.0))
    assert R.request_amount(pl, pl.buffer + 100.0) == pytest.approx(100.0)
    assert R.b_star(M.funded_terms("TS/std"))["b_star"] == pytest.approx(cap / 0.5)
    for m in M.MODE_CORNERS:
        if m.kind == M.FUNDED:
            assert math.isfinite(R.b_star(M.mode_corner_terms(m))["b_star"])


def test_lists_implied_close_only_boundary_ceiling() -> None:
    assert all(x["implied"] for x in R.part_a_rows()["implied_days"])
    assert not R.implied_days(ev(consistency=0.5, min_days=5))["implied"]
    assert M.close_only_corners() == (15, 17)
    listing = R.boundary_listing()
    assert {(c["mode"], c["w"], c["r"]) for c in listing} == {(md, w, r) for md in ("L6", "L11") for w in (1.0, 2.0)
                                                              for r in (250.0, 500.0, 1000.0)}
    assert {c["boundary"] for c in listing if c["w"] == 1.0} == {True}
    assert {c["boundary"] for c in listing if c["w"] == 2.0} == {False}          # R-a: the ordinary pass ceiling
    assert {(c["mode"], c["w"], c["r"]) for c in R.boundary_cells()} == {(md, 1.0, r) for md in ("L6", "L11")
                                                                         for r in (250.0, 500.0, 1000.0)}
    for m in M.MODE_CORNERS:
        if m.kind == M.FUNDED:
            assert R.ceiling_cells(M.mode_corner_terms(m)) == []
    hb = replace(M.funded_terms("RE", M.STRICT), ceiling=1000.0)
    assert R.ceiling_cells(hb)


def test_boundary_exactness_by_walking_the_lattice() -> None:
    """The w = 2 cells overshoot T: a path reaching T - r and then winning 2 r ends above T (7 item 8's defect)."""
    t = M.eval_terms("L6")
    r, T = 500.0, float(t.target)
    B = -r
    while B + 2 * r < T:
        B += 2 * r
    assert B + 2 * r > T                                 # the pass lands above T, not at it


def test_n11_pro1_stated_from_the_firms_sentence() -> None:
    assert M.eval_terms("PRO1", M.STRICT).stated_fewest == 1                 # "One day pass", not the min-days field


def test_r_a_counts_boundary_steady_cells_only() -> None:
    c = R.oracle_count()
    cells = [x for x in R.coin_cells() if x["runs"] and x["kind"] == M.EVAL]
    close = set(M.close_only_corners())
    bset = {(b["index"], b["w"], b["r"]) for b in R.boundary_cells()}
    excluded = [x for x in cells if x["index"] not in close and x["coin"] == "gross" and x["policy"] == "steady"
                and (x["index"], x["w"], x["r"]) in bset]
    assert len(excluded) == 6
    assert c["pass_ceiling"] == sum(1 for x in cells if x["index"] not in close) - 6


def test_stated_fewest_check_fires_on_a_broken_record() -> None:
    for cfg in ("TS-S", "PRO1", "B20", "LU40", "LU50"):
        assert R.stated_check(M.eval_terms(cfg, M.STRICT if cfg in ("PRO1", "B20") else M.SINGLE))["equal"]
    with pytest.raises(R.StatedFewestMismatch):
        R.stated_check(replace(M.eval_terms("TS-S"), stated_fewest=1))


def test_r_flip_and_cuts() -> None:
    t = M.eval_terms("TS-S")
    rf = R.r_flip(M.EVAL, t, 1.0)
    assert rf["r_flip"] == pytest.approx(t.target / (rf["k"] * 1.0)) and rf["cut_by"] == "none"
    l6 = R.r_flip(M.EVAL, M.eval_terms("L6"), 1.0)
    assert l6["cut_by"] == "daily_limit" and l6["cut_at_start"] == pytest.approx(M.eval_terms("L6").dll)


def test_a19_parses_each_named_quote_and_refuses_a_broken_one(monkeypatch: pytest.MonkeyPatch) -> None:
    want = {"U-16.lock": 100.0, "U-29.lock": 100.0, "U-17.buffer": 2100.0, "U-17.share": 60.0,
            "U-22.min_high": 250.0, "U-22.min_low": 125.0, "U-24.limit_006": 5.0, "U-24.limit_dpp": 5.0,
            "U-28.dll": 1000.0, "U-30.minis": 2.0, "U-30.micros": 20.0}
    assert set(want) == set(M.A19)
    for k, v in want.items():
        assert M.quote_figure(k) == v, k
    from extended import firm_terms as FT

    rec = dict(FT._record())
    broken = dict(rec["mffu.builder50k.daily_loss_limit"])
    broken["quote"] = "no figure here"
    rec["mffu.builder50k.daily_loss_limit"] = broken
    monkeypatch.setattr(FT, "_record", lambda: rec)
    with pytest.raises(TermParseError):
        M.quote_figure("U-28.dll")
    ver = dict(broken, status="verified", value="1000")
    rec["mffu.builder50k.daily_loss_limit"] = ver
    with pytest.raises(TermParseError, match="verified now"):
        M.quote_figure("U-28.dll")


# ------------------------------------------------------------------------------------------------- T-6, part B


def test_part_b_hand_computed_cells() -> None:
    tv = M.tick_values()
    st = R.State("fresh", 0.0, 2000.0, None, 5, 50, "ratio")
    z = R.size(st, 1000.0, 100, "MNQ", "topstep", M.EVAL)
    assert z["micros"] == min(int(1000.0 // (100 * tv["MNQ"])), 50) == 20 and z["binding"] == "dollar_risk"
    z = R.size(st, 2000.0, 20, "MNQ", "topstep", M.EVAL)
    assert z["micros"] == 50 and z["binding"] == "allowance"
    z = R.size(st, 2000.0, 100, "NQ", "topstep", M.EVAL)
    assert z["minis"] == 4 and z["binding"] == "dollar_risk"
    z = R.size(st, 1700.0, 100, "mixed", "topstep", M.EVAL)
    assert (z["minis"], z["micros"]) == (3, 4) and z["realised_risk"] == pytest.approx(1700.0)
    st2 = R.State("dll", 0.0, 2000.0, 1000.0, 5, 50, "ratio")
    z = R.size(st2, 2000.0, 100, "mixed", "topstep", M.EVAL)
    assert z["binding"] == "daily_limit" and z["realised_risk"] == pytest.approx(1000.0)
    st3 = R.State("room", 0.0, 600.0, None, 5, 50, "ratio")
    assert R.size(st3, 2000.0, 100, "mixed", "topstep", M.EVAL)["binding"] == "room"
    sa = M.registered_stand_aside()["combine"]
    assert R.size(st, 1000.0, int(sa[1]) - 5, "mixed", "topstep", M.EVAL)["stood_aside"]
    assert not R.size(st, 1000.0, int(sa[1]), "mixed", "topstep", M.EVAL)["stood_aside"]


def test_part_b_u26_two_counts() -> None:
    pro_s = M.funded_terms("PRO", M.STRICT).allowance
    pro_l = M.funded_terms("PRO", M.LENIENT).allowance
    s = R.State("flat", 0.0, 2000.0, None, pro_s.minis, pro_s.micros, pro_s.counting)
    l = R.State("flat", 0.0, 2000.0, None, pro_l.minis, pro_l.micros, pro_l.counting)
    zs = R.size(s, 2000.0, 50, "MNQ", "mffu", M.FUNDED)
    zl = R.size(l, 2000.0, 50, "MNQ", "mffu", M.FUNDED)
    assert zs["micros"] == pro_s.micros == 3 and zl["micros"] == 30
    zm = R.size(s, 1500.0, 100, "mixed", "mffu", M.FUNDED)
    assert zm["minis"] + zm["micros"] <= 3


def test_part_b_constants_read_from_their_modules() -> None:
    from propedge.campaign import sizing

    sa = M.registered_stand_aside()
    assert sa["d117_headroom"] == sizing.DEFAULT_HEADROOM_FRAC and M.micros_per_mini() == sizing.MICROS_PER_MINI
    st = R.State("fresh", 0.0, 2000.0, None, 5, 50, "ratio")
    hc = R.headroom_cap(st)
    assert hc["d117_cap_me"] == math.floor(sizing.DEFAULT_HEADROOM_FRAC * 50)
    assert hc["registered_cap_me"] == math.floor(sa["headroom"] * 50)


def test_part_b_states_and_cost_share() -> None:
    m = next(x for x in M.MODE_CORNERS if x.mode == "TS/std")
    sts = R.states(m, M.mode_corner_terms(m))
    assert [s.minis for s in sts] == [n for _, n in M.funded_terms("TS/std").allowance.ladder]
    z = R.size(sts[0], 500.0, 100, "mixed", "topstep", M.FUNDED)
    mnq, nq = M.topstep_round_turn()
    slip = M.fill_slippage()
    want = (z["minis"] * nq + z["micros"] * mnq + (slip["entry_slippage_ticks"] + slip["stop_slippage_ticks"])
            * (z["minis"] * M.tick_values()["NQ"] + z["micros"] * M.tick_values()["MNQ"])) / z["realised_risk"]
    assert z["cost_share"] == pytest.approx(want)


def test_oracle_count_within_the_declared_maximum() -> None:
    c = R.oracle_count()
    assert c["N"] <= M.declared("oracle.n_max")
    assert c["gross_runs"] <= 2016 and c["costed_runs"] <= 3240
    assert c["supremum"] == sum(1 for x in R.coin_cells() if x["runs"] and x["mode"] == "TS" and x["kind"] == M.EVAL)
