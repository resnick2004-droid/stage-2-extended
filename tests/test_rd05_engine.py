"""RD-05's T-1, T-3 (the coin side), T-7 and T-8 (`prereg/RD-05_firm_modes.md` 17.3): the coin engine A-0 against the
vendored functions, its additions on scripted and toy streams, the flip schedule, the costed coin and `RI`'s peak law.
Synthetic only, on the `build_toys` seed (section 15); no bar, no result file; small runs (fast tier).

* T-1: with `spec` None the copies equal `propsim.simulate_combine` / `simulate_xfa` bit for bit; the guard refuses a
  changed vendored source; the recomposition proof holds and catches an unmarked change.
* T-3 (coin side): the base coin at `TS` equals the vendored functions at Stage 2's rules (the evaluation exactly;
  the Standard funded path differing only by A-16's request-day exclusion, the listed known difference); every
  addition on scripted streams -- the soft daily limit, the static floor and its move at a payout, the minimum days,
  the lifespan, inactivity on the costed coin, U-15's base, U-27's close-only floor, the buffer and cadence, Pro's
  clock, Builder's cycle and count, the Daily path at both U-22 ends, the request-day exclusion, LucidFlex's count, the
  single-day ceiling. **Not here:** each coin form against its account class (part F's classes are not built).
* T-7: `k` and `r_flip` from part A; one trade a session; the cuts counted; a flip cell equal to its steady cell on
  every account until the first flip trade (with `k` 0 it is the steady cell); R-1's entry rule, one toy case each way.
* T-8: the costed coin -- `n` from the room, costs inside the room, its mean P&L equal to minus its mean costs within
  its error, a stood-aside session counted toward inactivity; `RI`'s peak law against a fine random walk; the read set.
"""
from __future__ import annotations

import inspect
import math
from datetime import datetime, timedelta

import numpy as np
import pytest

from extended import modes_engine as E
from extended import modes_news as NW
from extended import modes_rules as R
from extended import modes_terms as M

vp = E._vp
TOYS = M.seed("build_toys")


def toy(*key: int) -> np.random.Generator:
    return np.random.default_rng([TOYS, *key])


def corner(mode: str, kind: str, c: str = M.SINGLE) -> M.ModeCorner:
    return next(m for m in M.MODE_CORNERS if m.mode == mode and m.kind == kind and m.corner == c)


class Scripted:
    """A scripted coin stream: `pnl[d]` the gross P&L of session d's trade for every account (NaN: no trade); the
    room and the floor are the engine's (the draw never clamps). Fair-check facts with p 1/2, span 1."""

    def __init__(self, days: list[float]):
        self.days = days
        self.last = {}

    def __call__(self, n, day, slot, cushion):
        x = self.days[day] if day < len(self.days) else 0.0
        pnl = np.full(n, float(x))
        pnl = np.maximum(pnl, -np.maximum(cushion, 0.0)) if np.isfinite(x) else pnl
        self.last = {"p": np.full(n, 0.5), "span": np.ones(n), "hit": pnl > 0, "gross": pnl, "cost": np.zeros(n),
                     "risk": np.ones(n), "room_cut": np.zeros(n, bool), "flip": np.zeros(n, bool),
                     "contracts": np.zeros(n, int), "peak": np.maximum(pnl, 0.0), "peak_F": np.full(n, 0.5)}
        return pnl


def run_eval_scripted(mode: str, c: str, days: list[float], n: int = 1) -> dict:
    m = corner(mode, M.EVAL, c)
    spec = E.EvalSpec(M.mode_corner_terms(m), 1.0, 500.0)
    return E.simulate_combine(spec.rules(), spec.policy_obj(), 0.0, n, rng=toy(0), draw=Scripted(days),
                              max_days=len(days), spec=spec)


def run_funded_scripted(mode: str, c: str, days: list[float], n: int = 1) -> dict:
    m = corner(mode, M.FUNDED, c)
    spec = E.FundedSpec(M.mode_corner_terms(m), 1.0, 500.0)
    return E.simulate_xfa(spec.rules(), spec.policy_obj(), 0.0, n, rng=toy(0), draw=Scripted(days),
                          horizon_days=len(days), spec=spec)


# ------------------------------------------------------------------------------------------------- T-1


@pytest.mark.parametrize("w,r", [(1.0, 1500.0), (1.5, 750.0), (3.0, 250.0), (2.0, 2000.0)])
def test_t1_bit_for_bit_with_spec_none(w: float, r: float) -> None:
    pol, rules = vp.Policy(rr=w, risk=r), vp.Rules()
    for ours, theirs, kw in ((E.simulate_combine, vp.simulate_combine, {"max_days": 504}),
                             (E.simulate_xfa, vp.simulate_xfa, {"horizon_days": 504})):
        a = theirs(rules, pol, 0.0, 400, rng=toy(1), **kw)
        b = ours(rules, pol, 0.0, 400, rng=toy(1), **kw)
        assert set(a) == set(b)
        for k in a:
            assert np.array_equal(a[k], b[k]), (ours.__name__, k)


def test_t1_coin_draw_is_random_draw_at_k0() -> None:
    pol = vp.Policy(rr=2.0, risk=750.0)
    a = vp.RandomDraw(pol, 0.0, toy(2), "truncate", "drift")
    b = E.CoinDraw(2.0, 750.0, toy(2))
    cush = np.linspace(-10.0, 3000.0, 300)
    for d in range(20):
        assert np.array_equal(a(300, d, 0, cush), b(300, d, 0, cush))


def test_t1_guard_and_recomposition(monkeypatch: pytest.MonkeyPatch) -> None:
    assert E.recomposition_problems() == []
    E.check_vendored_sources()
    monkeypatch.setitem(E.VENDORED_SHA256, "simulate_combine", "0" * 64)
    with pytest.raises(RuntimeError, match="REFUSED"):
        E.check_vendored_sources()


def test_t1_recomposition_catches_an_unmarked_change() -> None:
    from extended.campaign import recomposition_problems

    src = inspect.getsource(E.simulate_combine).replace("best_day[alive] = np.maximum(best_day[alive], day_pnl[alive])",
                                                        "best_day[alive] = np.maximum(best_day[alive], 2 * day_pnl[alive])")
    ns: dict = {}
    exec(compile(src, "<changed>", "exec"), {**E.__dict__}, ns)          # noqa: S102 -- a test's own text
    changed = ns["simulate_combine"]
    changed.__source__ = src
    import linecache

    linecache.cache["<changed>"] = (len(src), None, src.splitlines(True), "<changed>")
    assert recomposition_problems(changed, vp.simulate_combine, (E.MARKER,))


# ------------------------------------------------------------------------------------------------- T-3, the base coin


def test_t3_base_coin_at_ts_evaluation_equals_the_vendored() -> None:
    from propedge.contract.adapter import rules_from_ledger

    t = M.eval_terms("TS-S")
    for w, r in ((1.0, 1500.0), (2.0, 500.0)):
        spec = E.EvalSpec(t, w, r)
        a = vp.simulate_combine(rules_from_ledger(), vp.Policy(rr=w, risk=r), 0.0, 500, rng=toy(3), max_days=504)
        b = E.run_eval(spec, 500, toy(3))
        for k in a:
            assert np.array_equal(a[k], b[k]), k


def test_t3_base_coin_at_ts_standard_differs_only_by_the_request_day() -> None:
    """The known difference (13.1 (d)): A-16's exclusion. With it switched off the funded coin is the vendored one."""
    from dataclasses import replace

    from propedge.contract.adapter import rules_from_ledger

    t = M.funded_terms("TS/std")
    spec = E.FundedSpec(replace(t, request_day_excluded=False), 1.0, 500.0)
    a = vp.simulate_xfa(rules_from_ledger(), vp.Policy(rr=1.0, risk=500.0), 0.0, 500, rng=toy(4), horizon_days=504)
    b = E.run_funded(spec, 500, toy(4))
    for k in a:
        assert np.array_equal(a[k], b[k]), k
    c = E.run_funded(E.FundedSpec(t, 1.0, 500.0), 500, toy(4))
    assert np.array_equal(a["first_payout_day"], c["first_payout_day"])      # the first window has no request before
    assert not np.array_equal(a["n_payouts"], c["n_payouts"])                # later windows lose the excluded day


# ------------------------------------------------------------------------------------------------- T-3, the additions


def test_t3_soft_daily_limit_and_static_floor() -> None:
    # L6: static floor at -2000, soft DLL 1000: a 1500 loss is cut to the limit, the account not failed
    o = run_eval_scripted("L6", M.SINGLE, [-1500.0, 500.0])
    assert o["B"][0] == pytest.approx(-500.0) and not o["failed"][0]
    assert o["F"][0] == pytest.approx(-2000.0)                       # static: never moves
    o = run_eval_scripted("L10", M.SINGLE, [1000.0, 1000.0, -100.0])
    assert o["F"][0] == pytest.approx(0.0)                           # trailing, locked at the start


def test_t3_static_funded_floor_moves_to_zero_at_a_payout() -> None:
    days = [400.0] * 5 + [-100.0]
    o = run_funded_scripted("L6/std", M.STRICT, days)
    assert o["n_payouts"][0] == 1 and o["F"][0] == pytest.approx(0.0)


def test_t3_min_days_and_consistency_base() -> None:
    # RE: 4 minimum days, 30 % share; one 3,000 day then small wins: strict base (net) needs the total at 10,000
    o = run_eval_scripted("RE", M.STRICT, [3000.0] + [100.0] * 10)
    assert not o["passed"][0]
    o = run_eval_scripted("RE", M.STRICT, [800.0] * 4)
    assert o["passed"][0] and o["pass_day"][0] == 3                  # passes on the fourth day (min days, 30 %)
    o3 = run_eval_scripted("RE", M.STRICT, [1000.0] * 3)
    assert not o3["passed"][0]                                       # three days: the minimum days owed
    # U-15 lenient: the winning days' sum as the base -- a losing day does not shrink it
    days = [950.0, 950.0, 950.0, -1000.0, 950.0, 300.0]
    s, l = run_eval_scripted("RE", M.STRICT, days), run_eval_scripted("RE", M.LENIENT, days)
    assert not s["passed"][0] and l["passed"][0]


def test_t3_lifespan_and_close_only() -> None:
    t = M.eval_terms("L6")
    days = [10.0] * (t.lifespan + 3)
    o = run_eval_scripted("L6", M.SINGLE, days)
    assert o["expired"][0] and not o["unresolved"][0] and int(o["days"][0]) == t.lifespan
    # B20 lenient: the floor checked at the close only -- a loss through the floor is not truncated
    o = run_eval_scripted("B20", M.LENIENT, [-2500.0])
    assert o["failed"][0] and o["B"][0] == pytest.approx(-2500.0)
    o = run_eval_scripted("B20", M.STRICT, [-2500.0])
    assert o["B"][0] == pytest.approx(-1000.0) and not o["failed"][0]   # U-28 strict: the soft limit


def test_t3_buffer_gate_and_cadence() -> None:
    # RE: the buffer 2,100 plus the minimum 500, not before a session after the first trade; later 500 since
    o = run_funded_scripted("RE", M.STRICT, [2700.0, 0.0, 600.0, 0.0])
    assert o["first_payout_day"][0] == 1 and o["n_payouts"][0] >= 1
    o = run_funded_scripted("RE", M.LENIENT, [2700.0, 0.0])
    assert o["gross_paid"][0] == pytest.approx(600.0)                # lenient: everything above the buffer
    o = run_funded_scripted("RE", M.STRICT, [4200.0, 0.0])
    assert o["gross_paid"][0] == pytest.approx(min(0.5 * 4200.0, 2000.0))


def test_t3_pro_clock() -> None:
    t = M.funded_terms("PRO", M.STRICT)
    days = [3200.0] + [0.0] * (t.wait_first + 1)
    o = run_funded_scripted("PRO", M.STRICT, days)
    assert o["first_payout_day"][0] == t.wait_first


def test_t3_builder_cycle_and_count() -> None:
    t = M.funded_terms("B20", M.LENIENT)
    days = [1500.0, 1500.0, 1500.0] + [0.0] * 3
    o = run_funded_scripted("B20", M.LENIENT, days)
    assert o["first_payout_day"][0] == 2
    days = ([1300.0, 1300.0, 1300.0, 0.0] + [600.0, 600.0, 0.0] * 12)
    o = run_funded_scripted("B20", M.LENIENT, days)
    assert o["n_payouts"][0] == t.max_payouts and o["count_end"][0]


def test_t3_daily_path_both_ends() -> None:
    days = [2600.0, 0.0, 0.0]
    s = run_funded_scripted("L10/day", M.STRICT, days)
    l = run_funded_scripted("L10/day", M.LENIENT, days)
    assert l["first_payout_day"][0] == 0 and l["gross_paid"][0] == pytest.approx(600.0)
    assert s["first_payout_day"][0] == 1 and s["gross_paid"][0] == pytest.approx(600.0)
    assert s["F"][0] == pytest.approx(0.0)                           # a daily payout sets the floor to $0


def test_t3_request_day_exclusion() -> None:
    t = M.funded_terms("TS/std")
    win = t.winning_day_min + 50.0
    days = [win] * 5 + [win] * 5 + [0.0]
    o = run_funded_scripted("TS/std", M.SINGLE, days)
    assert o["first_payout_day"][0] == 4 and o["n_payouts"][0] == 1   # the 6th session counts toward no window
    days = [win] * 5 + [win] * 6 + [0.0]
    o = run_funded_scripted("TS/std", M.SINGLE, days)
    assert o["n_payouts"][0] == 2


def test_t3_lucid_count_and_ceiling() -> None:
    t = M.funded_terms("LU")
    o = run_funded_scripted("LU", M.SINGLE, [400.0] * (t.winning_days * (t.max_payouts + 2)))
    assert o["n_payouts"][0] == t.max_payouts and o["count_end"][0]
    f = M.funded_terms("RE", M.STRICT)
    o = run_funded_scripted("RE", M.STRICT, [f.ceiling + 1234.0, 0.0])
    assert o["moved_live"][0] and o["forfeit"][0] == pytest.approx(1234.0) and o["n_payouts"][0] == 0


# ------------------------------------------------------------------------------------------------- T-7


def test_t7_flip_schedule_from_part_a() -> None:
    for mode, kind in (("TS", M.EVAL), ("RE", M.EVAL), ("TS/std", M.FUNDED), ("PRO", M.FUNDED)):
        m = corner(mode, kind, M.SINGLE if mode.startswith("TS") else M.STRICT)
        t = M.mode_corner_terms(m)
        sp = E.spec_for(m, 1.5, 500.0, policy="flip")
        rf = R.r_flip(kind, t, 1.5)
        assert sp.k == rf["k"] and sp.r_flip == pytest.approx(rf["r_flip"])


def test_t7_flip_equals_steady_until_the_first_flip_trade_and_counts_cuts() -> None:
    m = corner("L10", M.EVAL)
    t = M.mode_corner_terms(m)
    steady = E.run_eval(E.EvalSpec(t, 1.0, 500.0), 300, toy(7))
    flip = E.run_eval(E.EvalSpec(t, 1.0, 500.0, policy="flip"), 300, toy(7))
    k0 = E.run_eval(E.EvalSpec(t, 1.0, 500.0, policy="flip"), 300, toy(7), horizon=0)
    assert np.array_equal(k0["B"], np.zeros(300))
    rf = R.r_flip(M.EVAL, t, 1.0)
    assert rf["cut_by"] == "daily_limit"
    assert int(np.sum(flip["room_cuts"])) == int(np.sum(flip["flip_trades"])) > 0   # every flip trade cut to the DLL
    assert int(np.max(flip["trades"] - flip["days"])) <= 0                          # one trade a session
    assert not np.array_equal(steady["B"], flip["B"])
    d = E.CoinDraw(1.0, 500.0, toy(8), k=0)
    f = E.CoinDraw(1.0, 500.0, toy(8), k=3, r_flip=900.0)
    cush = np.full(50, 5000.0)
    assert not np.array_equal(d(50, 0, 0, cush), f(50, 0, 0, cush))
    for day in range(3, 10):                                                         # after the window: identical
        assert np.array_equal(E.CoinDraw(1.0, 500.0, toy(9))(50, day, 0, cush),
                              E.CoinDraw(1.0, 500.0, toy(9), k=3, r_flip=900.0)(50, day, 0, cush))


def test_t7_r1_entry_at_the_order_live_time() -> None:
    before, after = NW.window_minutes()
    rel = datetime(2026, 1, 7, 13, 0)
    w = [NW.window_at(rel)]
    latency = 5
    # an alert before the window whose order goes live inside it: refused
    assert NW.entry_refused(rel - timedelta(minutes=before + latency - 1), latency, w)
    # an alert inside the window whose order goes live after it: not refused
    assert not NW.entry_refused(rel + timedelta(minutes=after - 1), latency, w)
    # a working order at the window's start is cancelled; a position open at the start is flattened at that bar
    alert = rel - timedelta(minutes=before + latency + 3)
    assert NW.order_cancelled(alert, latency, None, w)                                  # working at the start
    assert not NW.order_cancelled(alert, latency, alert + timedelta(minutes=latency), w)  # filled before it
    assert NW.forced_flat(rel - timedelta(minutes=30), rel + timedelta(minutes=30), w) == w[0]
    assert NW.forced_flat(rel + timedelta(minutes=after + 1), rel + timedelta(minutes=60), w) is None


def test_t7_news_reach() -> None:
    assert NW.reaches("RI", M.FUNDED, M.STRICT) and NW.reaches("PRO", M.FUNDED, M.LENIENT)
    assert NW.reaches("RE", M.FUNDED, M.STRICT) and not NW.reaches("RE", M.FUNDED, M.LENIENT)
    for cfg in ("TS-S", "L6", "L10", "B20", "LU40"):
        assert not NW.reaches(cfg, M.FUNDED, M.STRICT)
    assert not NW.reaches("RI", M.EVAL, M.STRICT)


# ------------------------------------------------------------------------------------------------- T-8


def test_t8_costed_coin_room_and_costs() -> None:
    t = M.eval_terms("TS-S")
    d = E.CostedCoinDraw(1.0, 1000.0, 100, t.allowance, "topstep", M.EVAL, toy(10))
    d.set_tier(4, np.zeros(4))
    rooms = np.array([10.0, 120.0, 600.0, 5000.0])
    pnl = d(4, 0, 0, rooms)
    assert np.isnan(pnl[0])                                          # no size fits: no trade
    ok = ~np.isnan(pnl)
    assert np.all(pnl[ok] >= -rooms[ok] - 1e-9)                       # costs inside the room
    assert np.all(d.table.realised[d.last["index"]][ok] <= 1000.0 + 1e-9)
    tb = d.table
    assert np.all(np.diff(tb.stopout) > 0)


def test_t8_costed_mean_is_minus_its_costs() -> None:
    t = M.eval_terms("TS-S")
    d = E.CostedCoinDraw(1.5, 500.0, 50, t.allowance, "topstep", M.EVAL, toy(11))
    d.set_tier(200_000, np.zeros(200_000))
    x = d(200_000, 0, 0, np.full(200_000, 1e6))
    idx = d.last["index"]
    cost = np.where(x > 0, d.table.cost_win[idx], d.table.cost_loss[idx])
    se = float(np.std(x) / math.sqrt(len(x)))
    assert abs(float(np.mean(x)) + float(np.mean(cost))) < 4 * se


def test_t8_stood_aside_counts_toward_inactivity() -> None:
    m = corner("RE", M.EVAL, M.STRICT)
    t = M.mode_corner_terms(m)
    spec = E.EvalSpec(t, 1.0, 250.0, coin="costed", stop=50)
    # a stop below the registered cost floor is never taken: every session is a no-trade session
    sa = M.registered_stand_aside()["combine"]
    spec_low = E.EvalSpec(t, 1.0, 250.0, coin="costed", stop=int(sa[1]) - 5)
    o = E.run_eval(spec_low, 20, toy(12))
    assert o["inactive"].all() and int(np.max(o["days"])) == t.inactivity
    o = E.run_eval(spec, 20, toy(12), horizon=3)
    assert not o["inactive"].any()


def test_t8_ri_peak_law_against_a_random_walk() -> None:
    """9.2: a losing trade's highest point, racing -a against +b, by a fine symmetric random walk (build_toys)."""
    rng = toy(13)
    a, b, step = 20, 40, 1
    peaks = []
    n_paths = 6000
    pos = np.zeros(n_paths, int)
    peak = np.zeros(n_paths, int)
    done = np.zeros(n_paths, bool)
    lost = np.zeros(n_paths, bool)
    while not done.all():
        mv = rng.choice((-step, step), size=n_paths)
        pos = np.where(done, pos, pos + mv)
        peak = np.maximum(peak, pos)
        lost |= ~done & (pos <= -a)
        done |= (pos <= -a) | (pos >= b)
    peaks = peak[lost]
    for x in (5, 10, 20, 30):
        emp = float(np.mean(peaks >= x))
        law = float(E.peak_survival(x, a, b))
        se = math.sqrt(law * (1 - law) / len(peaks))
        assert abs(emp - law) < 4 * se + 0.01, (x, emp, law)
    s = np.array([0.1, 0.5, 0.9])
    assert np.allclose(E.peak_survival(E.peak_inverse(s, a, b), a, b), s)


def test_t8_read_set_on_r_and_r_flip() -> None:
    f = M.funded_terms("RI", M.STRICT)
    assert R.ri_read_set(f, 1.0, 1000.0) and not R.ri_read_set(f, 1.0, 1001.0)
    rows = [c for c in R.coin_cells() if c["index"] == 36 and c["coin"] == "gross"]
    assert all(not c["runs"] for c in rows if c["policy"] == "flip")
    assert {(c["w"], c["r"]) for c in rows if c["runs"]} == {(w, r) for w in M.grid_w() for r in M.grid_r()
                                                              if (w + 1) * r <= f.mll}


# ------------------------------------------------------------------------------------------------- Q-138 cycle 1


def test_b2_costed_ri_rows_36_and_37_run_with_their_peaks() -> None:
    """B-2 / R-c: the costed coin at RI's funded corners draws its losing-trade peaks at a = r', b = w r' and runs its
    oracles clean; the read set is (w + 1) r' + stop-out costs <= D."""
    from extended import modes_oracles as O

    for idx in (36, 37):
        m = M.MODE_CORNERS[idx]
        t = M.mode_corner_terms(m)
        cells = [c for c in R.coin_cells() if c["index"] == idx and c["coin"] == "costed"]
        assert any(c["runs"] for c in cells) and any(not c["runs"] for c in cells)
        for c in cells:
            if c["runs"]:
                assert R.ri_read_set_costed(m, t, c["w"], c["r"], c["stop"])
        c = next(c for c in cells if c["runs"])
        spec = E.FundedSpec(t, c["w"], c["r"], coin="costed", stop=c["stop"])
        out = E.run_funded(spec, 2000, toy(40, idx), toy(41, idx))
        O.oracle_rows(M.FUNDED, out, t, N=R.oracle_count()["N"], mode=m.mode, boundary=False, close_only=False)
        assert out["fair"]["trades"] > 0 and set(out["exact"].values()) == {0}


def test_s4_last_gate_is_the_last_to_turn_true() -> None:
    """S-4: consistency holds early, lapses on a large day, holds again last -- it is the gate that held last."""
    o = run_eval_scripted("TS", M.SINGLE, [200.0, 200.0, 200.0, 200.0, 2000.0, 300.0, 600.0])
    assert o["passed"][0] and o["raised"][0]
    assert o["last_gate"][0] == "consistency_target"
    assert o["gate_rise"]["consistency_target"][0] > o["gate_rise"]["base_target"][0]


def test_s8_untraded_costed_session_is_no_cycle_day() -> None:
    m = corner("B20", M.FUNDED, M.STRICT)
    spec = E.FundedSpec(M.mode_corner_terms(m), 1.0, 500.0, coin="costed", stop=100)
    st = spec.start(3, E.CostedCoinDraw(1.0, 500.0, 100, spec.t.allowance, spec.t.commission, M.FUNDED, toy(42)))
    st.traded = np.array([True, False, True])
    w_days = np.array([2, 2, 2])
    spec.after_window(st, np.ones(3, bool), np.zeros(3), np.zeros(3, int), np.zeros(3, int), w_days)
    assert w_days.tolist() == [2, 1, 2]
    g = E.FundedSpec(M.mode_corner_terms(m), 1.0, 500.0)
    st = g.start(1, E.CoinDraw(1.0, 500.0, toy(43)))
    st.traded = np.array([False])
    w = np.array([2])
    g.after_window(st, np.ones(1, bool), np.zeros(1), np.zeros(1, int), np.zeros(1, int), w)
    assert w.tolist() == [2]                                          # the gross coin trades every live session


def test_s7_declared_streams_refuse_outside_step_2(monkeypatch: pytest.MonkeyPatch) -> None:
    for role in E.DECLARED_ROLES:
        with pytest.raises(RuntimeError, match="S-7"):
            E.stream(role, 0, 0)
    E.stream("build_toys", 0, 0)
    with pytest.raises(RuntimeError):
        E.allow_declared_streams("a test")
    monkeypatch.setitem(E._DECLARED_STREAMS, "cleared", False)
    E.allow_declared_streams("scripts/modes_coin.py main: step_problems(2) empty")
    assert E._DECLARED_STREAMS["cleared"]


def test_n3_dll_applies_at_a_close_only_corner() -> None:
    from dataclasses import replace

    t = replace(M.eval_terms("B20", M.LENIENT), dll=1000.0)
    spec = E.EvalSpec(t, 1.0, 500.0)
    st = spec.start(2, E.CoinDraw(1.0, 500.0, toy(44)))
    room = spec.room(st, np.array([5000.0, 5000.0]), np.array([0.0, -300.0]))
    assert room.tolist() == [1000.0, 700.0]
