"""Wave 3.2: the seed-paired runner and its journey (`extended/three_way_runner.py`, `three_way_journey.py`,
`three_way_s1.py`) on synthetic schedules with known answers -- no engine, no bar, no result; fast.

- **the exact program is the replay's law** -- on a tiny toy its expectation equals a brute-force enumeration of every
  outcome, exactly; on a sparse toy the simulation's mean is within four standard errors of it; the exact-centred null's
  terms are centred;
- **the antithetic pair sums correctly** -- one symmetric trade on a deep account: every unit's change and its twin's
  sum to zero; and the twin's pool is centred;
- **the pairing** -- the design and the four baselines read one coin field (a common moment is one key), the set must be
  exactly the four, the convention identical (a plant is the design's only); a stress applies to all alike;
- **choice 3** -- every key read carries its unit's start, and no two keys share a state across arms, starts and seeds;
- **the enforcement stream is apart** -- the denial ladder at q > 0 reads exactly the coin keys of q = 0, plus its own;
- **the refusals** -- overlapping positions, two trades at one moment, a window past the block's end, disjoint sets
  sharing a seed;
- **shift invariance where bars could be read (none are)** -- the modules import no bar reader; a unit's row is bit for
  bit unchanged by any change to the schedule outside its window; two real paths with one schedule (different walked
  ticks) give one martingale reading;
- **the readings** -- `journey_measures.coin_readings` reads the runner's matrix; P_B's two code paths agree.

Corrective cycle 1 (the red team's read of 746a245, `docs/reviews/BUILD_W32_H3_2026-11-19.md`):
- **B-1** -- the red team's forced-loss toy: every account fails on its first cushion-bound loss and is replaced; the
  journey's own race step (`_trade_mc`, `_trade_dp`) books exactly `race_net`'s changes on a grid of fractional cushions
  and unequal costs, forced to each side of p; the simulation equals the exact program on a toy whose cushion binds;
- **m-2** -- the walk: the simulation equals the exact program on a walk toy of step 2 with unequal costs; the exact
  program's walk step books `walk_net`'s net and worst change;
- **m-11, U** -- the exact program's `passed` (the red team's toy: 0.875) and its denial against the simulation's;
- **B-2** -- the guard checks every key's start and stores its declared sample only; the sample fits a worker's memory
  at every declared size; the packing is injective and its collision bound is printed;
- **m-10** -- held-out sessions refused unless the joint test's declaration is named, the first held-out day included.
"""
from __future__ import annotations

import ast
import itertools
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from extended import journey_measures as JM
from extended import three_way_journey as J
from extended import three_way_keys as K
from extended import three_way_runner as R
from extended import three_way_s1 as S1
from extended import three_way_seeds as S

ROOT = Path(__file__).resolve().parent.parent
SEED = S.issue("tests")
PART = S.PARTS["tests"]
RULES = J.ToyRules(combine_fee=20, billing=21, target=100, mll=100, dll=None, activation_fee=20, funded_mll=100,
                   win_day=50, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
DEEP = J.ToyRules(combine_fee=20, billing=21, target=1e9, mll=1e9, dll=None, activation_fee=20, funded_mll=1e9,
                  win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1.0, split=1.0, payout_lag=1)


def toy(name: str, every: int, n: int = 90, g: int = 10, l: int = 10, decision: int = 600, cost: float = 0.0,
        reason: str = "target", **kw) -> J.Schedule:
    return J.Schedule(name, tuple(J.Trade(session=s, decision=decision, entry=decision + 5, exit=decision + 50,
                                          exit_reason=reason, g=g, l=l, tick_value=5.0, entry_cost=cost,
                                          x_target=cost, x_stop=cost * 2, x_flat=cost * 2, **kw)
                                  for s in range(0, n, every)))


def baselines(n: int = 90) -> dict[str, J.Schedule]:
    return {"naive_coin": toy("naive_coin", 5, n, decision=700), "p14": toy("p14", 6, n, g=20, l=10, decision=600),
            "p15": toy("p15", 7, n, decision=800), "p16": toy("p16", 4, n, g=10, l=20, decision=900)}


def plan(**kw) -> R.Plan:
    base = dict(seed=SEED, part=PART, history=0, starts=(0, 5, 11), seed_indices=tuple(range(24)), horizon=63,
                block_sessions=90, budget=60.0)
    base.update(kw)
    return R.Plan(**base)


# ------------------------------------------------------------------------------------------------ the exact program


def _brute(schedule: J.Schedule, rules: J.ToyRules, start: int, horizon: int, budget: float) -> float:
    """E[P_B] by enumerating every win/loss pattern of the window's race trades: each pattern's journey replayed by
    the simulation with its outcome forced (uniforms just below 0 or 1), weighted by the pattern's probability."""
    trades = schedule.window(start, horizon).trades
    total = mass = 0.0
    for pattern in itertools.product((True, False), repeat=len(trades)):
        w = 1.0
        L = J.fresh(1, rules)
        for k in range(1, horizon + 1):
            L.day, L.dead, L.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
            for t, win in zip(trades, pattern):
                if t.session != start + k - 1:
                    continue
                room = J._room(L, rules)
                if L.dead[0] or L.stopped[0] or not J._l_fill(t, room, 0.0)[0] * t.tvn > J.EPS:
                    w *= 1.0 if win else 0.0                    # a trade not raced: one pattern carries the weight
                    if not (L.dead[0] or L.stopped[0]) and room[0] > J.EPS:
                        J._settle(L, np.ones(1, bool), -room, rules)   # failed at the fill (floor-bound: no limit here)
                    continue
                Lt = J._barrier(t, room, 0.0)
                p = float(Lt[0] / (Lt[0] + t.g))
                w *= p if win else 1 - p
                ch = (t.g * t.tvn - t.x_target) if win else (-Lt[0] * t.tvn - t.x_stop)
                J._settle(L, np.ones(1, bool), np.array([-t.entry_cost + ch]), rules)
            L = J._close(L, k, rules, J.ArmSpec(), budget, None, dp=False)
        total += w * L.ahead[0] / 3.0
        mass += w
    assert abs(mass - 1.0) < 1e-12, mass
    return total


def _forced(monkeypatch, u: float) -> None:
    """Every uniform the journey reads pinned to u (the scalar and the vectorised path alike)."""
    from extended import three_way_fastkeys as F

    monkeypatch.setattr(K, "uniforms", lambda key, n=1, twin=False: np.full(n, u))
    monkeypatch.setattr(F, "uniforms",
                        lambda keys, n=1, twin=False, first=0: np.full((np.asarray(keys).shape[0], n), u))


def test_the_rules_by_hand(monkeypatch) -> None:
    """Every outcome forced (the uniforms pinned just above 0, then just below 1): the journey's closes computed by
    hand from the toy rules -- the fee on day 0, a pass at 100 with its activation fee, the funded account's winning
    days, a payout of half the balance after two, its cash a close later; and the losing journey's breaches, each
    replaced by a new evaluation at its close."""
    sch = toy("hand", 1, 12)
    p = plan(starts=(0,), seed_indices=(0,), horizon=9, block_sessions=12, budget=None)
    _forced(monkeypatch, 2.0 ** -53)
    rec = R.run(sch, RULES, p)[0]
    assert rec.rel[0].tolist() == [-20, -20, -40, -40, -40, 10, 10, 85, 85, 172.5]
    assert rec.first_pass[0] == 2 and rec.first_pay[0] == 5
    assert rec.arrivals[0] == [(5, 50.0), (7, 75.0), (9, 87.5)]
    _forced(monkeypatch, 1.0 - 2.0 ** -53)
    rec = R.run(sch, RULES, p)[0]
    assert rec.rel[0].tolist() == [-20, -20, -40, -40, -60, -60, -80, -80, -100, -100]
    assert rec.first_pass[0] == -1 and rec.accounts[0] == 4


def test_the_exact_program_is_a_brute_force_enumeration() -> None:
    sch = J.Schedule("tiny", toy("a", 9, 70, g=20, l=10, cost=1.0).trades
                     + toy("b", 9, 70, g=10, l=25, cost=0.5, decision=900).trades[:3])   # asymmetric brackets
    for start in (0, 4):
        n = len(sch.window(start, 63).trades)
        assert n <= 11
        dp = J.expect(sch, RULES, start, 63, block_sessions=70, budget=60.0)
        assert abs(dp["total"] - 1.0) < 1e-12
        assert dp["p_b"] == pytest.approx(_brute(sch, RULES, start, 63, 60.0), abs=1e-12)


def test_the_simulation_matches_the_exact_program() -> None:
    sch = toy("sparse", 4, 90)
    p = plan(starts=(3,), seed_indices=tuple(range(400)))
    x = R.matrix(R.run(sch, RULES, p), R.p_b)
    dp = J.expect(sch, RULES, 3, 63, block_sessions=90, budget=60.0)
    se = x.std() / np.sqrt(x.size)
    assert abs(x.mean() - dp["p_b"]) < 4 * se + 1e-12, (x.mean(), dp["p_b"], se)


def test_the_exact_centred_null_is_centred() -> None:
    f, b = toy("f", 4, 90), toy("b", 3, 90, g=20, l=10, decision=700)
    p = plan(starts=(0, 7, 13), seed_indices=tuple(range(160)))
    xf, xb = R.matrix(R.run(f, RULES, p), R.p_b), R.matrix(R.run(b, RULES, p), R.p_b)
    theta = R.exact_centres(f, b, RULES, p)
    d = (xf - xb) - theta[:, None]
    assert abs(d.mean()) < 4 * d.std() / np.sqrt(d.size)
    assert np.all(np.abs(theta) <= 1.0)


# ------------------------------------------------------------------------------------------------ the nulls


def test_the_antithetic_pair_sums_correctly() -> None:
    sch = toy("one", 1, 3, g=12, l=12)
    p = plan(starts=(0,), seed_indices=tuple(range(64)), horizon=1, block_sessions=3, budget=None)
    x, xt = R.antithetic(sch, DEEP, p, lambda r: r.balance)
    assert np.all(x + xt == 0) and set(np.unique(x)) == {-60.0, 60.0}
    sch2 = toy("pool", 3, 90, g=20, l=10)
    a, at = R.antithetic(sch2, RULES, plan(seed_indices=tuple(range(96))), R.p_b)
    d = (a - at).mean(axis=0)                                           # one replicate a seed
    assert abs(d.mean()) < 4 * d.std(ddof=1) / np.sqrt(d.size)


def test_the_disjoint_null_and_its_refusal() -> None:
    sch = toy("d", 3, 90)
    x1, x2 = R.disjoint(sch, RULES, plan(seed_indices=tuple(range(32))), range(32, 64), R.p_b)
    assert x1.shape == x2.shape and not np.array_equal(x1, x2)
    with pytest.raises(ValueError):
        R.disjoint(sch, RULES, plan(seed_indices=tuple(range(32))), range(31, 63), R.p_b)


# ------------------------------------------------------------------------------------------------ the pairing


def test_the_pairing_and_choice_3() -> None:
    design = toy("design", 3, 90, decision=700)                       # shares naive coin's moments on some sessions
    xs, guard = R.paired(design, baselines(), RULES, plan(), R.p_b, guard=K.KeyGuard())
    assert set(xs) == {"design", *R.BASELINES} and all(v.shape == (3, 24) for v in xs.values())
    starts = {K.key_start(k) for k in guard.keys()}
    assert starts == {0, 5, 11}
    # a moment the design and naive coin share is one key, read by both arms
    shared = {t.moment for t in design.trades} & {t.moment for t in baselines()["naive_coin"].trades}
    assert shared
    moments = [k for k in guard.keys() if k[1] == K.KEY_KINDS["coin"][0]]
    assert len(moments) == len(set(moments))
    with pytest.raises(ValueError):
        R.paired(design, {k: v for k, v in baselines().items() if k != "p15"}, RULES, plan(), R.p_b)
    with pytest.raises(ValueError):
        R.paired(design, baselines(), RULES, plan(), R.p_b, design_arm=J.ArmSpec(worse_ticks=1))
    planted, _ = R.paired(design, baselines(), RULES, plan(), R.p_b, design_arm=J.ArmSpec(plant_eps=0.2))
    assert planted["design"].mean() > xs["design"].mean()             # P3's plant moves the design only
    assert np.array_equal(planted["p14"], xs["p14"])


def test_the_stress_applies_to_every_arm_alike() -> None:
    design = toy("design", 3, 90, cost=0.5)
    base = {k: replace(v, trades=tuple(replace(t, entry_cost=0.5) for t in v.trades)) for k, v in baselines().items()}
    out = R.stress(design, base, RULES, plan(seed_indices=tuple(range(8))), R.p_b)
    assert sorted(out) == sorted(R.stress_arms()) == ["missed_0.1", "worse_1", "worse_2"]   # m-7: the missed arm too
    assert all(set(v) == {"design", *R.BASELINES} for v in out.values())
    assert R.stress_cells() == 5 * 3 and R.stress_arms()["missed_0.1"].missed_q == 0.10


def test_the_enforcement_stream_is_apart_from_the_coin() -> None:
    sch = toy("payer", 2, 90, g=20, l=10)
    p = plan(seed_indices=tuple(range(32)))
    g0, g1 = K.KeyGuard(), K.KeyGuard()
    R.run(sch, RULES, p, J.ArmSpec(), g0)
    R.run(sch, RULES, p, J.ArmSpec(enforcement_q=0.5), g1)
    coin = K.KEY_KINDS["coin"][0]
    c0 = {k for k in g0.keys() if k[1] == coin}
    c1 = {k for k in g1.keys() if k[1] == coin}
    e1 = {k for k in g1.keys() if k[1] == K.KEY_KINDS["enforce"][0]}
    assert c0 == c1 and e1 and not {k for k in g0.keys() if k[1] != coin}
    # the exact program prices the ladder: denials only lower P_B, and the law stays a law
    sparse = toy("payer", 6, 90, g=20, l=10)
    dp0 = J.expect(sparse, RULES, 0, 63, block_sessions=90, budget=60.0)
    dp1 = J.expect(sparse, RULES, 0, 63, block_sessions=90, arm=J.ArmSpec(enforcement_q=0.5), budget=60.0)
    assert dp1["p_b"] < dp0["p_b"] and abs(dp1["total"] - 1) < 1e-12


# ------------------------------------------------------------------------------------------------ the refusals


def test_overlap_and_shared_moments_and_windows_are_refused() -> None:
    a = J.Trade(session=1, decision=600, entry=605, exit=700, exit_reason="target", g=10, l=10, tick_value=5.0)
    b = replace(a, decision=650, entry=655, exit=720)
    with pytest.raises(ValueError, match="1.6"):
        J.Schedule("overlap", (a, b))
    J.Schedule("touching", (a, replace(b, entry=700)))
    with pytest.raises(ValueError, match="moment"):
        J.Schedule("same moment", (a, replace(a, entry=800, exit=900)))
    with pytest.raises(ValueError):
        plan(starts=(30,))                                             # 30 + 63 > 90
    with pytest.raises(ValueError):
        J.Trade(session=1, decision=600, entry=605, exit=700, exit_reason="expired", g=10, l=10, tick_value=5.0)


# ------------------------------------------------------------------------------------------------ shift invariance


BAR_MODULES = {"extended.walker", "extended.triggers", "extended.synthetic_bars", "extended.features", "pandas",
               "propedge"}
#: the reader is imported by the runner for its authorisation only (m-10's held-out refusal); no read call is made


def test_the_runner_modules_import_no_bar_reader() -> None:
    for name in ("three_way_keys", "three_way_seeds", "three_way_redraw", "three_way_journey", "three_way_runner",
                 "three_way_s1", "three_way_stats"):
        tree = ast.parse((ROOT / "extended" / f"{name}.py").read_text(encoding="utf-8"))
        got = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                got |= {a.name for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                got |= {f"{node.module}.{a.name}" for a in node.names} | {node.module or ""}
        assert not any(g == m or g.startswith(m + ".") for g in got for m in BAR_MODULES), (name, got)
        src = (ROOT / "extended" / f"{name}.py").read_text(encoding="utf-8")
        assert "read_bars" not in src and "read_walks" not in src and "authorise_engine_read" not in src
        if name != "three_way_runner":
            assert "extended.reader" not in got and "reader" not in {g.split(".")[-1] for g in got}, (name, got)


def test_a_unit_reads_only_its_own_window() -> None:
    sch = toy("w", 2, 90)
    p = plan(starts=(10,), seed_indices=tuple(range(16)))
    x = R.matrix(R.run(sch, RULES, p), R.p_b)
    outside = tuple(replace(t, g=t.g * 3, l=t.l + 7) if not (10 <= t.session < 73) else t for t in sch.trades)
    junk = tuple(J.Trade(session=s, decision=1000, entry=1001, exit=1100, exit_reason="flatten", g=4, l=4,
                         tick_value=50.0, walk_n=5) for s in (0, 9, 73, 89))
    y = R.matrix(R.run(J.Schedule("w", outside + junk), RULES, p), R.p_b)
    assert np.array_equal(x, y)


def test_two_real_paths_with_one_schedule_give_one_martingale_reading() -> None:
    base = toy("path", 3, 90)
    walked_a = J.Schedule("path", tuple(replace(t, walked_ticks=float(t.g)) for t in base.trades))
    walked_b = J.Schedule("path", tuple(replace(t, walked_ticks=-float(t.l)) for t in base.trades))
    p = plan(seed_indices=tuple(range(16)))
    xa = R.matrix(R.run(walked_a, RULES, p), R.p_b)
    xb = R.matrix(R.run(walked_b, RULES, p), R.p_b)
    assert np.array_equal(xa, xb)
    aw = J.ArmSpec(reading="as_walked")
    ya = R.matrix(R.run(walked_a, RULES, p, aw), lambda r: r.rel[:, -1])
    yb = R.matrix(R.run(walked_b, RULES, p, aw), lambda r: r.rel[:, -1])
    assert not np.array_equal(ya, yb)                                  # the beside reading does read the path


# ------------------------------------------------------------------------------------------------ the readings


def test_the_coin_readings_read_the_runners_matrix_and_p_b_agrees() -> None:
    sch = toy("r", 3, 90)
    p = plan(seed_indices=tuple(range(20)))
    recs = R.run(sch, RULES, p)
    x = R.matrix(recs, R.p_b)
    out = JM.coin_readings(x, lag=63)
    assert out["n_starts"] == 3 and out["n_seeds"] == 20
    pooled = JM.p_bankroll([r for rec in recs for r in rec.rel], 60.0)["P"]
    assert pooled == pytest.approx(x.mean(), abs=1e-12)


def test_s1_histories_and_their_designs_run_through_the_runner() -> None:
    params = S1.S1Params(n_sessions=90)
    hist = S1.generate(SEED, PART, 0, params)
    spec = S1.DesignSpec("s1design", stream="A", walk_step=2)
    sch = S1.schedule(spec, hist)
    assert any(t.law == "walk" for t in sch.trades) and any(t.law == "race" for t in sch.trades)
    base = {k: S1.schedule(v, hist) for k, v in S1.toy_baselines().items()}
    xs, guard = R.paired(sch, base, RULES, plan(seed_indices=tuple(range(8))), R.p_b)
    assert len(xs) == 5 and guard.states
    swapped = S1.schedule(replace(spec, stream="B"), hist.swap())
    assert swapped.trades == sch.trades                                # the stream swap is a symmetry of schedules


# ------------------------------------------------------------------------------------------------ corrective cycle 1




def test_b1_the_forced_loss_toy_fails_and_replaces_every_account(monkeypatch) -> None:
    """The red team's probe: mll 103 at $5 a tick (20.6 ticks), l = g = 30, one trade a session, every race lost. The
    first loss is cushion-bound (20.6 ticks), ends exactly on the floor, and the account is replaced at that close --
    every session, with its fee; nothing is stranded a fraction of a tick above the floor."""
    rules = J.ToyRules(combine_fee=20, billing=21, target=1000, mll=103, dll=None, activation_fee=20, funded_mll=103,
                       win_day=50, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = toy("zombie", 1, 70, g=30, l=30)
    _forced(monkeypatch, 1.0 - 2.0 ** -53)
    rec = R.run(sch, rules, plan(starts=(0,), seed_indices=(0,), horizon=63, block_sessions=70, budget=None))[0]
    assert rec.accounts[0] == 63                                      # one new evaluation at every close
    assert rec.rel[0].tolist() == [-20.0 * (k + 1) for k in range(64)]
    assert rec.balance[0] == 0.0                                      # the last close's fresh account


def test_m1_the_journeys_race_books_race_net_on_a_fractional_grid(monkeypatch) -> None:
    """`_trade_mc` and `_trade_dp` themselves: over fractional cushions and unequal costs, with uniforms forced just
    below and just above p, the booked change is `race_net`'s win and worst change (in ticks x tick dollars)."""
    from fractions import Fraction

    from extended import three_way_redraw as RD

    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=1e6, dll=None, activation_fee=1, funded_mll=1e6,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    n = 0
    for l, g, room4, e4, xt4, xs4 in itertools.product((8, 20), (6, 30), (13, 37, 81, 161, 400), (0, 1, 3), (0, 2),
                                                        (1, 5)):
        tv = 1.25
        e, xt, xs = e4 / 4 * tv, xt4 / 4 * tv, xs4 / 4 * tv
        room = room4 / 4 * tv
        r = RD.race_net(l, g, Fraction(room4, 4), Fraction(e4, 4), Fraction(xt4, 4), Fraction(xs4, 4), None)
        t = J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="target", g=g, l=l, tick_value=tv,
                    entry_cost=e, x_target=xt, x_stop=xs)
        L0 = J.fresh(1, rules)
        L0.bal = np.array([room - rules.mll])
        if r is None:                                                    # no take at the fill: failed there (B-2)
            L0.day, L0.dead, L0.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
            coins = J.CoinLanes(SEED, PART, 0, 0, (0,), None, False)
            J._trade_mc(L0, t, rules, J.ArmSpec(), coins)
            if room > J.EPS:
                assert L0.bal[0] - (room - rules.mll) == pytest.approx(-room, abs=1e-9) and bool(L0.dead[0])
                assert L0.ffail[0] == 1
            continue
        p = float(RD.race(l, g, Fraction(room4 - e4, 4), Fraction(xs4, 4), None)[0])
        for u, change in ((np.nextafter(p, 0), float(-Fraction(e4, 4) + g - Fraction(xt4, 4)) * tv),
                          (np.nextafter(p, 1), float(r[2]) * tv)):
            L = J.fresh(1, rules)
            L.bal = np.array([room - rules.mll])
            L.day, L.dead, L.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
            coins = J.CoinLanes(SEED, PART, 0, 0, (0,), None, False)
            coins.coin = lambda t_, kind, n_=1, lanes=None, _u=u: np.array([[_u]])
            J._trade_mc(L, t, rules, J.ArmSpec(), coins)
            assert L.bal[0] - (room - rules.mll) == pytest.approx(change, abs=1e-9), (l, g, room4, e4, xt4, xs4, u)
        L = J.fresh(1, rules)
        L.bal = np.array([room - rules.mll])
        L.day, L.dead, L.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
        out = J._trade_dp(L, t, rules, J.ArmSpec())
        ch = out.bal - (room - rules.mll)
        assert float((out.w * ch).sum()) == pytest.approx(float(r[1]) * tv, abs=1e-9)
        assert float(ch.min()) == pytest.approx(float(r[2]) * tv, abs=1e-9)
        n += 1
    assert n > 100


def test_m1_the_simulation_matches_the_exact_program_where_the_cushion_binds() -> None:
    rules = J.ToyRules(combine_fee=20, billing=21, target=180, mll=103, dll=55, activation_fee=20, funded_mll=103,
                       win_day=40, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = toy("binds", 3, 90, g=14, l=30, cost=1.06)
    p = plan(starts=(2,), seed_indices=tuple(range(600)))
    x = R.matrix(R.run(sch, rules, p), R.p_b)
    dp = J.expect(sch, rules, 2, 63, block_sessions=90, budget=60.0)
    se = x.std() / np.sqrt(x.size)
    assert abs(x.mean() - dp["p_b"]) < 4 * se + 1e-12, (x.mean(), dp["p_b"], se)
    accts = np.concatenate([r.accounts for r in R.run(sch, rules, p)])
    assert accts.mean() > 1                                           # failing accounts are replaced


def _walk_toy(n: int = 90, every: int = 3) -> J.Schedule:
    return J.Schedule("walk", tuple(J.Trade(session=s, decision=700, entry=705, exit=790, exit_reason="max_hold",
                                            g=8, l=12, tick_value=5.0, entry_cost=0.5, x_target=0.25, x_stop=1.5,
                                            x_flat=0.75, walk_step=2, walk_n=9) for s in range(0, n, every)))


def test_m2_the_simulations_walk_step_books_the_walks_outcome() -> None:
    """`_trade_mc`'s walk branch itself: on 3000 lanes of random uniforms at fractional cushions, each lane's booked
    change is -entry + the walk's value x tick dollars - its exit's own cost (target, stop or flatten), the value and
    exit from `three_way_redraw.walk_outcome` on the same uniforms; and the mean change is `walk_net`'s net within four
    standard errors."""
    from fractions import Fraction

    from extended import three_way_redraw as RD

    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=1e6, dll=None, activation_fee=1, funded_mll=1e6,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    rng = np.random.default_rng(K.seed_key(SEED, "test", test=S.TEST_IDS["walk_oracle"], replicate=1))
    t = _walk_toy(3, 1).trades[0]
    n_l = 3000
    for room4 in (9, 23, 47, 300):
        room = room4 / 4 * t.tvn
        U = rng.random((n_l, t.walk_n))
        L = J.fresh(n_l, rules)
        L.bal = np.full(n_l, room - rules.mll)
        L.day, L.dead, L.stopped = np.zeros(n_l), np.zeros(n_l, bool), np.zeros(n_l, bool)
        coins = J.CoinLanes(SEED, PART, 0, 0, range(n_l), None, False)
        coins.coin = (lambda t_, kind, n_=1, lanes=None, first=0, record=True, _U=U:
                      _U[np.arange(n_l) if lanes is None else lanes][:, first:first + n_])
        J._trade_mc(L, t, rules, J.ArmSpec(), coins)
        ch = L.bal - (room - rules.mll)
        l_fill = min(t.l, (room - t.entry_cost - max(t.x_stop, t.x_flat)) / t.tvn)
        Lt = min(t.l, (room - t.entry_cost - t.x_stop) / t.tvn)
        for k in range(0, n_l, 37):
            if not l_fill * t.tvn > J.EPS:
                assert ch[k] == pytest.approx(-room, abs=1e-9)          # failed at the fill
                continue
            v, kind = RD.walk_outcome(U[k], t.g, Lt, t.walk_step)
            cost = {"target": t.x_target, "stop": t.x_stop, "time": t.x_flat}[kind]
            want = max(-t.entry_cost + float(v) * t.tvn - cost, -room)  # the flatten clipped at the floor
            assert ch[k] == pytest.approx(want, abs=1e-9), (room4, k)
        r = RD.walk_net(t.l, t.g, Fraction(room4, 4), t.walk_n, t.walk_step, Fraction(1, 10), Fraction(1, 20),
                        Fraction(3, 10), Fraction(3, 20))
        assert abs(ch.mean() - float(r[1]) * t.tvn) < 4 * ch.std() / np.sqrt(n_l) + 1e-9, room4


def test_m2_the_walk_simulation_matches_the_exact_program_on_a_small_toy() -> None:
    rules = J.ToyRules(combine_fee=20, billing=21, target=60, mll=91, dll=None, activation_fee=20, funded_mll=91,
                       win_day=30, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = J.Schedule("walk", tuple(replace(t, g=12, walk_n=5) for t in _walk_toy(90, 6).trades))
    p = plan(starts=(1,), seed_indices=tuple(range(800)))
    recs = R.run(sch, rules, p)
    dp = J.expect(sch, rules, 1, 63, block_sessions=90, budget=60.0)
    assert dp["states"] < 50_000
    fp = np.concatenate([r.first_pass for r in recs]) > 0
    q = dp["passed"]
    assert 0.05 < q < 0.95 and abs(fp.mean() - q) < 4 * np.sqrt(q * (1 - q) / fp.size), (fp.mean(), q)
    x = R.matrix(recs, R.p_b)
    assert abs(x.mean() - dp["p_b"]) < 4 * x.std() / np.sqrt(x.size) + 1e-12


def test_m2_the_exact_programs_walk_step_is_walk_net() -> None:
    from fractions import Fraction

    from extended import three_way_redraw as RD

    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=1e6, dll=None, activation_fee=1, funded_mll=1e6,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    for room4, n_steps, xf4 in itertools.product((9, 23, 47, 81, 300), (1, 4, 9), (3, 13)):
        # x_flat 0.75 below x_stop 1.5, and 3.25 above it (H3-A's order): the barrier is the stop's in both (RB-1)
        t = replace(_walk_toy(3, 1).trades[0], walk_n=n_steps, tick_value=1.0, x_flat=xf4 / 4)
        room = room4 / 4
        L = J.fresh(1, rules)
        L.bal = np.array([room - rules.mll])
        L.day, L.dead, L.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
        out = J._trade_dp(L, t, rules, J.ArmSpec())
        ch = out.bal - (room - rules.mll)
        r = RD.walk_net(t.l, t.g, Fraction(room4, 4), n_steps, t.walk_step, Fraction(1, 2), Fraction(1, 4),
                        Fraction(3, 2), Fraction(xf4, 4))
        if r is None:
            continue
        assert float((out.w * ch).sum()) == pytest.approx(float(r[1]), abs=1e-9), (room4, n_steps, xf4)
        assert float(ch.min()) == pytest.approx(float(r[2]), abs=1e-9), (room4, n_steps, xf4)


def test_m11_the_exact_programs_passed_survives_its_merges() -> None:
    """The red team's toy: three race trades at p = 1/2 (the cushion-bound loss of 8 ticks against a target of 8) on
    accounts that fail at their first loss and pass at their first win, so P(a pass by close 3) = 1 - 1/8. A funded
    account that fails is replaced by an evaluation whose state equals a never-passed one: before the fix the merge
    kept one representative's first pass (0.625)."""
    rules = J.ToyRules(combine_fee=20, billing=21, target=40, mll=40, dll=None, activation_fee=20, funded_mll=40,
                       win_day=1e9, payout_days=99, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = toy("pass", 1, 3, g=8, l=10)
    assert J.expect(sch, rules, 0, 3, block_sessions=3)["passed"] == pytest.approx(0.875, abs=1e-12)
    recs = R.run(sch, rules, plan(starts=(0,), seed_indices=tuple(range(2000)), horizon=3, block_sessions=3,
                                  budget=None))
    assert abs((recs[0].first_pass > 0).mean() - 0.875) < 4 * np.sqrt(0.875 * 0.125 / 2000)


def test_u_the_exact_programs_denial_is_the_simulations() -> None:
    sch = toy("payer", 4, 90, g=20, l=10)
    arm = J.ArmSpec(enforcement_q=0.5)
    p = plan(starts=(0,), seed_indices=tuple(range(800)))
    x = R.matrix(R.run(sch, RULES, p, arm), R.p_b)
    dp = J.expect(sch, RULES, 0, 63, block_sessions=90, arm=arm, budget=60.0)
    se = x.std() / np.sqrt(x.size)
    assert abs(x.mean() - dp["p_b"]) < 4 * se + 1e-12, (x.mean(), dp["p_b"], se)
    assert dp["p_b"] < J.expect(sch, RULES, 0, 63, block_sessions=90, budget=60.0)["p_b"]


def test_b2_the_guard_checks_every_start_and_stores_its_sample_only() -> None:
    sch = toy("g", 2, 90)
    p = plan(starts=(0, 5, 11), seed_indices=tuple(range(100)))
    g = K.KeyGuard.sampled(p.starts, p.seed_indices)
    R.run(sch, RULES, p, J.ArmSpec(), g)
    stored = g.keys()
    assert {K.key_start(k) for k in stored} == {0}
    assert {k[4] for k in stored} == set(range(K.SAMPLE_SEEDS))       # the first SAMPLE_SEEDS seed indices
    assert g.checked > len(stored) * 3                                # every key checked, few stored
    with pytest.raises(ValueError, match="N-2"):
        g.add(K.Unit(SEED, PART, 0, 3, 5).coin_key(7, K.RACE), 6, 3)
    assert K.packing_problems() == []
    assert K.collision_bound(10 ** 11) < 1.5e-17                      # n^2 / 2^129 at n = 1e11 (about 1.47e-17)


def test_b2_the_guards_sample_fits_a_workers_memory_at_every_declared_size() -> None:
    """Every part's sample (one start, SAMPLE_SEEDS seeds, every arm, every session of the horizon, at most four
    trades a session, every draw kind read once a trade) at the stored bytes a key measured here, within 1.25 GB a
    worker less the process base the cost probe measures (taken at 0.4 GB, the note's assumption, as a ceiling)."""
    import importlib.util
    import tracemalloc

    spec = importlib.util.spec_from_file_location("three_way_arith_for_guard",
                                                  ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py")
    arith = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arith)
    tracemalloc.start()
    g = K.KeyGuard()
    for m in range(5000):
        g.add(K.Unit(SEED, PART, 0, m % 64, 0).coin_key(m, K.RACE), 0, m % 64)
    per_key = tracemalloc.get_traced_memory()[0] / 5000
    tracemalloc.stop()
    for name, R_, arms, M, T, h in arith.parts():
        keys = K.SAMPLE_SEEDS * arms * h * arith.TAU * 2           # a race and a side (or missed) draw a trade
        assert keys * per_key <= (1.25 - 0.4) * 2 ** 30, (name, keys, per_key)


def test_m10_held_out_sessions_are_refused_unless_the_joint_test_is_named() -> None:
    days = np.arange(np.datetime64("2023-09-01"), np.datetime64("2024-03-01"), dtype="datetime64[D]")
    days = days[np.is_busday(days)][:90]
    last_search = int(np.flatnonzero(days <= np.datetime64("2023-12-29"))[-1])
    ok_start = last_search - 63 + 1                                   # its window ends 2023-12-29
    R.Plan(seed=SEED, part=PART, history=0, starts=(ok_start,), seed_indices=(0,), horizon=63, block_sessions=90,
           dates=tuple(days))
    first_held = int(np.flatnonzero(days >= np.datetime64("2024-01-02"))[0])
    assert days[first_held] == np.datetime64("2024-01-02")
    with pytest.raises(R.HeldOutRefused, match="m-10"):               # the window's last session is 2024-01-02 itself
        R.Plan(seed=SEED, part=PART, history=0, starts=(first_held - 62,), seed_indices=(0,), horizon=63,
               block_sessions=90, dates=tuple(days))
    from extended import reader

    with pytest.raises(reader.ReadRefused):                           # a name the reader does not authorise
        R.Plan(seed=SEED, part=PART, history=0, starts=(first_held - 62,), seed_indices=(0,), horizon=63,
               block_sessions=90, dates=tuple(days), held_out_declaration="prereg/F-99_no_such_test.md")
    late = np.arange(np.datetime64("2026-06-01"), np.datetime64("2026-09-30"), dtype="datetime64[D]")
    late = late[np.is_busday(late)][:70]
    with pytest.raises(R.HeldOutRefused, match="confirmation"):
        R.Plan(seed=SEED, part=PART, history=0, starts=(0,), seed_indices=(0,), horizon=21, block_sessions=70,
               dates=tuple(late), held_out_declaration="prereg/F-99_no_such_test.md")


def test_m16_the_history_nulls_pair_differs_in_its_stream_only() -> None:
    d, d2 = S1.stream_pair(S1.DesignSpec("D", stream="A", fixed_stop=10))
    assert d2.stream == "B" and replace(d2, stream="A", name="D") == d
    with pytest.raises(ValueError, match="m-16"):
        S1.stream_pair(S1.DesignSpec("D", stream="B"))


def test_n2_s1_holds_the_flatten_and_the_flat_gap() -> None:
    hist = S1.generate(SEED, PART, 3, S1.S1Params(n_sessions=60, rate=4.0, time_limit=400.0))
    sch = S1.schedule(S1.DesignSpec("n2", stream="A", per_session=6), hist)
    assert sch.trades and all(t.exit <= S1.SESSION_END for t in sch.trades)
    assert any(t.exit_reason == "flatten" for t in sch.trades)
    for day in sch.by_session.values():
        for a, b in zip(day, day[1:]):
            assert b.entry >= a.exit + S1.FLAT_GAP



def test_the_walk_read_in_chunks_is_the_walk_read_whole(monkeypatch) -> None:
    """`WALK_CHUNK` changes the cost, never the outcome: a walk schedule's records are bit for bit the same read one
    step, eight steps or every step at a time (the generator is counter-based; the lanes stop when absorbed)."""
    check_chunk_invariance(monkeypatch, J)


def check_chunk_invariance(monkeypatch, module) -> None:
    """The check, with the chunk set on `module` (the journey, or a mutant of it whose `_trade_mc` is patched in)."""
    rules = J.ToyRules(combine_fee=20, billing=21, target=60, mll=91, dll=None, activation_fee=20, funded_mll=91,
                       win_day=30, payout_days=2, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = J.Schedule("walk", tuple(replace(t, walk_n=40) for t in _walk_toy(90, 2).trades))
    p = plan(starts=(1, 7), seed_indices=tuple(range(50)))
    out = []
    for chunk in (1, 8, 10 ** 6):
        monkeypatch.setattr(module, "WALK_CHUNK", chunk)
        recs = R.run(sch, rules, p)
        out.append(np.concatenate([r.rel for r in recs]))
    assert np.array_equal(out[0], out[1]) and np.array_equal(out[1], out[2])



# ------------------------------------------------------------------------------------------------ corrective cycle 2 (RB-1)

#: the red team's re-read (docs/reviews/REREADS_W32_W34_O7_2026-11-20.md, RB-1): H3-A's declared costs a contract
H3A_COST, H3A_STOP, H3A_FLAT = 2.12, 2.12 + 5.0, 2.12 + 10.0


def _rb1_rules() -> J.ToyRules:
    return J.ToyRules(combine_fee=50, billing=21, target=3000, mll=2000, dll=1000.0, activation_fee=50, funded_mll=2000,
                      win_day=150, payout_days=5, payout_share=0.5, payout_cap=2000, split=0.9, payout_lag=1)


def _rb1_toy(walk: bool, l: int = 40, g: int = 40, per: int = 3, h: int = 63) -> J.Schedule:
    tr = []
    for sess in range(h):
        for j in range(per):
            d = 600 + 60 * j
            kw = (dict(exit_reason="max_hold", walk_step=4, walk_n=40) if walk else dict(exit_reason="target"))
            tr.append(J.Trade(session=sess, decision=d, entry=d + 5, exit=d + 50, g=g, l=l, tick_value=5.0,
                              entry_cost=H3A_COST, x_target=H3A_COST, x_stop=H3A_STOP, x_flat=H3A_FLAT, **kw))
    return J.Schedule("rb1", tuple(tr))


def _stranded_at_closes(monkeypatch, sch: J.Schedule, rules: J.ToyRules, seeds: int, forced: float | None = None):
    """Run the simulation; at every close record each lane's account and whether its room to the floor is inside the
    window (above EPS, at most the entry and the larger exit cost: no trade is taken there). Returns, per close after the
    first, the lanes that were inside the window at the previous close and still hold the same account -- under the
    first cycle's rule a state with no exit; under the ruling the next offered trade takes them at the engine's clip --
    and the records. Every session of the toys offers a trade."""
    if forced is not None:
        _forced(monkeypatch, forced)
    snaps = []
    orig = J._session

    def watch(L, trades, *a, **k):
        out = orig(L, trades, *a, **k)
        gap = out.bal - out.floor
        snaps.append((out.acct.copy(), (gap > J.EPS) & (gap <= H3A_COST + max(H3A_STOP, H3A_FLAT) + J.EPS)))
        return out

    monkeypatch.setattr(J, "_session", watch)
    p_ = plan(starts=(0,), seed_indices=tuple(range(seeds)), horizon=63, block_sessions=63, budget=None)
    rec = R.run(sch, rules, p_)[0]
    kept = [int((w0 & (a1 == a0)).sum()) for (a0, w0), (a1, _) in zip(snaps, snaps[1:])]
    return kept, rec, snaps


def test_rb1_no_unit_is_stranded_at_h3as_costs(monkeypatch) -> None:
    """The red team's toy at H3-A's costs (x_stop 7.12, x_flat 12.12), race and walk: at no close is any lane alive with
    room above EPS but at most the costs -- the share the re-read measured at 0.150 (race) and 0.838 (walk) is 0 -- and
    accounts fail and are replaced."""
    for walk in (False, True):
        kept, rec, snaps = _stranded_at_closes(monkeypatch, _rb1_toy(walk), _rb1_rules(), 400)
        assert max(kept) == 0, (walk, max(kept))                      # nobody stays in the window past a trade
        last_share = float(snaps[-1][1].mean())
        assert last_share < 0.02, (walk, last_share)                    # the re-read measured 0.150 and 0.838
        assert rec.accounts.mean() > 1.0, (walk, rec.accounts.mean())
        monkeypatch.undo()


def test_rb1_forced_losses_breach_and_replace_every_account(monkeypatch) -> None:
    """The third re-read's m-2: every outcome forced to lose, at H3-A's costs, on a floor nine full losses
    ($209.24 each) and $10 deep, no daily limit: each account takes nine full losses, sits $10 above its floor --
    inside the window, where no trade can be taken -- and fails at the fill on its next trade, its change the whole
    room (the clip), a breach, replaced at that close. For the race and the walk alike: failures at the fill, all
    replaced, every account's end one of them, nobody kept in the window past a trade."""
    rules = J.ToyRules(combine_fee=50, billing=21, target=3000, mll=9 * 209.24 + 10, dll=None, activation_fee=50,
                       funded_mll=2000, win_day=150, payout_days=5, payout_share=0.5, payout_cap=2000, split=0.9,
                       payout_lag=1)
    for walk in (False, True):
        kept, rec, snaps = _stranded_at_closes(monkeypatch, _rb1_toy(walk), rules, 4, forced=1.0 - 2.0 ** -53)
        assert max(kept) == 0, walk
        assert rec.fill_failures[0] >= 10, (walk, rec.fill_failures)
        assert np.array_equal(rec.accounts, rec.fill_failures), (walk, rec.accounts, rec.fill_failures)
        assert rec.first_pass[0] == -1
        monkeypatch.undo()
    # the clip itself, on one lane $10 above its floor: the change is exactly -$10 and the account is breached
    t = _rb1_toy(True).trades[0]
    L = _one_lane(rules, 10.0)
    coins = J.CoinLanes(SEED, PART, 0, 0, (0,), None, False)
    J._trade_mc(L, t, rules, J.ArmSpec(), coins)
    assert L.bal[0] - (10.0 - rules.mll) == pytest.approx(-10.0, abs=1e-12) and bool(L.dead[0]) and L.ffail[0] == 1


def test_rb1_the_exact_program_shares_the_fix() -> None:
    """The exact program against the simulation on a toy where the clip binds often (H3-A's costs, a small floor, a
    daily limit): on the first cycle's code in either one alone (the clipped lane left untaken) they disagree, so the
    cross-check sees this class of error (`test_three_way_mutations`' RB1a and RB1b)."""
    # one full loss (8 ticks, $40, and $9.24 of costs) leaves $2.76 of a $52 floor: every losing account then sits in
    # the clipped window, where the first cycle's rule stranded it and the ruling races it at the engine's clip
    rules = J.ToyRules(combine_fee=20, billing=21, target=30, mll=52, dll=None, activation_fee=20, funded_mll=52,
                       win_day=1e9, payout_days=99, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = J.Schedule("rb1dp", tuple(J.Trade(session=sess, decision=600, entry=605, exit=650, exit_reason="target",
                                            g=6, l=8, tick_value=5.0, entry_cost=H3A_COST, x_target=H3A_COST,
                                            x_stop=H3A_STOP) for sess in range(0, 40, 2)))
    p_ = plan(starts=(0,), seed_indices=tuple(range(3000)), horizon=21, block_sessions=40, budget=None)
    recs = R.run(sch, rules, p_)
    dp = J.expect(sch, rules, 0, 21, block_sessions=40)
    fp = (recs[0].first_pass > 0)
    q = dp["passed"]
    assert 0.05 < q < 0.95 and abs(fp.mean() - q) < 4 * np.sqrt(q * (1 - q) / fp.size), (fp.mean(), q)
    ahead = (recs[0].rel[:, 21] > J.TOL).mean()
    assert 0.0 <= ahead <= 1.0



def test_rb1_the_walks_flatten_is_clipped_at_the_floor_and_fails_the_account() -> None:
    """A walk whose barrier sits a fifth of a tick below the last lattice point, its uniforms forced to step up there
    and down elsewhere, ends at the time limit one residual above the barrier; its flatten cost (x_flat above x_stop)
    would pass the floor, so the change is clipped at the floor, exactly -room, and the account is breached -- the
    engine's clip, in the simulation and the exact program alike."""
    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=1e6, dll=None, activation_fee=1, funded_mll=1e6,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    t = J.Trade(session=0, decision=700, entry=705, exit=790, exit_reason="max_hold", g=40, l=40, tick_value=5.0,
                entry_cost=H3A_COST, x_target=H3A_COST, x_stop=H3A_STOP, x_flat=H3A_FLAT, walk_step=4, walk_n=12)
    room = H3A_COST + H3A_STOP + (8 + 0.2) * 5.0                        # L = 8.2 ticks: d = 2 steps, rho = 0.2 tick
    L = J.fresh(1, rules)
    L.bal = np.array([room - rules.mll])
    L.day, L.dead, L.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
    coins = J.CoinLanes(SEED, PART, 0, 0, (0,), None, False)
    # down, down to the bottom point, then up there (u below its p_up) and down again, ten times: a time exit at -8
    U = np.array([[0.9, 0.9] + [0.01, 0.9] * 5])
    from extended import three_way_redraw as RD

    v, kind = RD.walk_outcome(U[0], t.g, 8.2, t.walk_step)
    assert (kind, v) == ("time", -8.0)                                 # the flatten is what is clipped here
    coins.coin = lambda t_, kind, n_=1, lanes=None, first=0, record=True, _U=U: _U[:, first:first + n_]
    J._trade_mc(L, t, rules, J.ArmSpec(), coins)
    assert L.bal[0] - (room - rules.mll) == pytest.approx(-room, abs=1e-9) and bool(L.dead[0])
    L2 = J.fresh(1, rules)
    L2.bal = np.array([room - rules.mll])
    L2.day, L2.dead, L2.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
    out = J._trade_dp(L2, t, rules, J.ArmSpec())
    assert float((out.bal - (room - rules.mll)).min()) == pytest.approx(-room, abs=1e-9)
    assert (out.bal >= out.floor - J.EPS).all()



# ------------------------------------------------------------------------------------------------ the take at the fill


def _one_lane(rules, room):
    L = J.fresh(1, rules)
    L.bal = np.array([room - rules.mll])
    L.day, L.dead, L.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
    return L


def test_b2_an_account_below_its_costs_fails_at_the_fill_and_one_above_takes_the_race() -> None:
    """The template read's B-2 on the runner side, exact: at a floor room of e + max(x_stop, x_flat) - epsilon the
    account fails at the fill -- its change the whole room, a breach, one failure at the fill counted apart -- in the
    simulation and the exact program; at e + max x + epsilon it takes the race, its outcomes the race's own. A
    limit-bound lane below its costs ends its day instead."""
    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=500, dll=None, activation_fee=1, funded_mll=500,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    eps = 1e-4
    for reason in ("target", "flatten"):
        t = J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason=reason, g=10, l=10, tick_value=5.0,
                    entry_cost=H3A_COST, x_target=H3A_COST, x_stop=H3A_STOP, x_flat=H3A_FLAT, walk_step=2, walk_n=5)
        edge = H3A_COST + max(H3A_STOP, H3A_FLAT)
        L = _one_lane(rules, edge - eps)
        J._trade_mc(L, t, rules, J.ArmSpec(), J.CoinLanes(SEED, PART, 0, 0, (0,), None, False))
        assert L.bal[0] == pytest.approx(-rules.mll, abs=1e-9) and bool(L.dead[0]) and L.ffail[0] == 1, reason
        out = J._trade_dp(_one_lane(rules, edge - eps), t, rules, J.ArmSpec())
        assert len(out) == 1 and bool(out.dead[0]) and out.w[0] == 1.0 and out.ffail[0] == 1, reason
        L = _one_lane(rules, edge + eps)
        J._trade_mc(L, t, rules, J.ArmSpec(), J.CoinLanes(SEED, PART, 0, 0, (0,), None, False))
        assert L.ffail[0] == 0, reason                                 # taken: raced, not failed at the fill
        out = J._trade_dp(_one_lane(rules, edge + eps), t, rules, J.ArmSpec())
        assert len(out) >= 2 and abs(float(out.w.sum()) - 1.0) < 1e-12 and (out.ffail == 0).all(), reason
    dll_rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=500, dll=5.0, activation_fee=1, funded_mll=500,
                           win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    L = _one_lane(dll_rules, 300.0)
    J._trade_mc(L, t, dll_rules, J.ArmSpec(), J.CoinLanes(SEED, PART, 0, 0, (0,), None, False))
    assert bool(L.stopped[0]) and not bool(L.dead[0]) and L.bal[0] == 300.0 - 500           # the day ends, no trade


def test_m1_the_take_does_not_read_the_exit() -> None:
    """The template read's m-1 (its probe 1): two trades identical at the fill, one ending at its stop in the run, one
    at the flatten, at a room between e + x_stop and e + x_flat: both are refused alike (failed at the fill), never the
    stop taken and the flatten not; above e + x_flat both are taken."""
    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=500, dll=None, activation_fee=1, funded_mll=500,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    e, xs, xf = 2.0, 2.0, 6.0
    mk = lambda reason: J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason=reason, g=10, l=10,  # noqa
                                tick_value=5.0, entry_cost=e, x_target=e, x_stop=xs, x_flat=xf, walk_step=2, walk_n=5)
    for room in (e + xs + 2.5, e + xf + 2.5):                          # the probe's room, and one above both
        got = []
        for reason in ("stop", "flatten"):
            L = _one_lane(rules, room)
            J._trade_mc(L, mk(reason), rules, J.ArmSpec(), J.CoinLanes(SEED, PART, 0, 0, (0,), None, False))
            got.append(int(L.ffail[0]))
        assert got[0] == got[1], (room, got)
    assert got == [0, 0]


def test_m2_a_profit_level_races_at_min_g_level() -> None:
    """The template read's m-2 and the third re-read's m-3: a rule's exit at a profit level races at the as-placed
    target, never the walk; **the level is booked as the vendored engine books its need, net dollars of the trade**
    (`lockstep.need_to_pass`; `sizing`'s "settles ... at exactly the need"): G = min(g, (level + e + x_target) / tick
    dollars), a forced win books exactly +level, the exact program's win weight is L / (L + G); a level above what g
    nets leaves g; and a level at the account's need to pass passes it."""
    from extended import three_way_redraw as RD

    assert RD.law_of("profit_level") == "race"
    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=500, dll=None, activation_fee=1, funded_mll=500,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    for level, G, booked in ((16.0, 3.5, 16.0), (200.0, 10.0, -1.0 + 10.0 * 5.0 - 0.5)):
        t = J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="profit_level", g=10, l=10,
                    tick_value=5.0, entry_cost=1.0, x_target=0.5, x_stop=1.5, level=level)
        assert t.law == "race" and t.target(1.0, 0.5) == pytest.approx(G, abs=1e-12)
        L = _one_lane(rules, 400.0)
        coins = J.CoinLanes(SEED, PART, 0, 0, (0,), None, False)
        coins.coin = lambda t_, kind, n_=1, lanes=None, first=0, record=True: np.array([[2.0 ** -53]])
        J._trade_mc(L, t, rules, J.ArmSpec(), coins)
        assert L.bal[0] - (400.0 - 500) == pytest.approx(booked, abs=1e-12)
        out = J._trade_dp(_one_lane(rules, 400.0), t, rules, J.ArmSpec())
        wins = out.w[out.bal > 400.0 - 500]
        assert float(wins.sum()) == pytest.approx(10.0 / (10.0 + G), abs=1e-12)
    with pytest.raises(ValueError, match="carries its level"):
        J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="profit_level", g=10, l=10, tick_value=5.0)
    # a level at the need to pass (target 100 from a fresh account): a win nets exactly the need and the account passes
    pass_rules = J.ToyRules(combine_fee=1, billing=21, target=100, mll=500, dll=None, activation_fee=1,
                            funded_mll=500, win_day=1e9, payout_days=99, payout_share=0.5, payout_cap=1, split=1,
                            payout_lag=1)
    t = J.Trade(session=0, decision=600, entry=605, exit=650, exit_reason="profit_level", g=40, l=10, tick_value=5.0,
                entry_cost=1.0, x_target=0.5, x_stop=1.5, level=100.0)
    L = J.fresh(1, pass_rules)
    coins = J.CoinLanes(SEED, PART, 0, 0, (0,), None, False)
    coins.coin = lambda t_, kind, n_=1, lanes=None, first=0, record=True: np.array([[2.0 ** -53]])
    L.day, L.dead, L.stopped = np.zeros(1), np.zeros(1, bool), np.zeros(1, bool)
    J._trade_mc(L, t, pass_rules, J.ArmSpec(), coins)
    assert L.bal[0] == pytest.approx(100.0, abs=1e-12)
    L = J._close(L, 1, pass_rules, J.ArmSpec(), None, coins, dp=False)
    assert L.first_pass[0] == 1


def test_m4_the_journeys_walk_with_a_profit_level() -> None:
    """The third re-read's m-4 (a): a walk trade carrying a level walks to its fractional target G = (level + e +
    x_target) / tick dollars, in the simulation (each lane's change from `walk_outcome` at G on the same uniforms) and
    in the exact program (its law `walk_net` at that G, net and worst change, exactly)."""
    from fractions import Fraction

    from extended import three_way_redraw as RD

    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=1e6, dll=None, activation_fee=1, funded_mll=1e6,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    t = replace(_walk_toy(3, 1).trades[0], level=13.0, walk_n=9)       # G = (13 + 0.5 + 0.25) / 5 = 2.75 ticks
    G = t.target(t.entry_cost, t.x_target)
    assert G == pytest.approx(2.75, abs=1e-12) and t.g == 8
    rng = np.random.default_rng(K.seed_key(SEED, "test", test=S.TEST_IDS["walk_oracle"], replicate=2))
    n_l = 2000
    for room4 in (23, 47, 300):
        room = room4 / 4 * t.tvn
        U = rng.random((n_l, t.walk_n))
        L = J.fresh(n_l, rules)
        L.bal = np.full(n_l, room - rules.mll)
        L.day, L.dead, L.stopped = np.zeros(n_l), np.zeros(n_l, bool), np.zeros(n_l, bool)
        coins = J.CoinLanes(SEED, PART, 0, 0, range(n_l), None, False)
        coins.coin = (lambda t_, kind, n_=1, lanes=None, first=0, record=True, _U=U:
                      _U[np.arange(n_l) if lanes is None else lanes][:, first:first + n_])
        J._trade_mc(L, t, rules, J.ArmSpec(), coins)
        ch = L.bal - (room - rules.mll)
        Lt = min(t.l, (room - t.entry_cost - t.x_stop) / t.tvn)
        for k in range(0, n_l, 41):
            v, kind = RD.walk_outcome(U[k], G, Lt, t.walk_step)
            cost = {"target": t.x_target, "stop": t.x_stop, "time": t.x_flat}[kind]
            assert ch[k] == pytest.approx(max(-t.entry_cost + float(v) * t.tvn - cost, -room), abs=1e-9), (room4, k)
        out = J._trade_dp(_one_lane(rules, room), t, rules, J.ArmSpec())
        chd = out.bal - (room - rules.mll)
        r = RD.walk_net(t.l, t.g, Fraction(room4, 4), t.walk_n, t.walk_step, Fraction(1, 10), Fraction(1, 20),
                        Fraction(3, 10), Fraction(3, 20), g_cap=Fraction(11, 4))
        assert float((out.w * chd).sum()) == pytest.approx(float(r[1]) * t.tvn, abs=1e-9), room4
        assert float(chd.min()) == pytest.approx(float(r[2]) * t.tvn, abs=1e-9), room4


def test_m4_the_walks_clip_where_the_daily_limit_binds() -> None:
    """The third re-read's m-4 (b): a walk whose flatten cost would pass the daily limit's room -- the limit, not the
    floor, the nearer barrier -- is clipped at that room: the day ends at the limit, the account lives (the engine's
    `max(pnl, -(dll + day_pnl))`), in the simulation and the exact program."""
    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=1000, dll=50.24, activation_fee=1, funded_mll=1000,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    t = J.Trade(session=0, decision=700, entry=705, exit=790, exit_reason="max_hold", g=40, l=40, tick_value=5.0,
                entry_cost=H3A_COST, x_target=H3A_COST, x_stop=H3A_STOP, x_flat=H3A_FLAT, walk_step=4, walk_n=12)
    L = _one_lane(rules, 900.0)                                        # the floor $900 away, the limit $50.24
    coins = J.CoinLanes(SEED, PART, 0, 0, (0,), None, False)
    U = np.array([[0.9, 0.9] + [0.01, 0.9] * 5])                       # to the bottom point and back: a time exit
    coins.coin = lambda t_, kind, n_=1, lanes=None, first=0, record=True, _U=U: _U[:, first:first + n_]
    J._trade_mc(L, t, rules, J.ArmSpec(), coins)
    assert L.day[0] == pytest.approx(-50.24, abs=1e-9) and bool(L.stopped[0]) and not bool(L.dead[0])
    out = J._trade_dp(_one_lane(rules, 900.0), t, rules, J.ArmSpec())
    assert float(out.day.min()) == pytest.approx(-50.24, abs=1e-9) and (out.day >= -50.24 - J.EPS).all()
    assert not out.dead.any()


def test_n3_the_failures_at_the_fill_are_reported_and_kept_exactly() -> None:
    """n-3: the failures at the fill are printed beside each arm's matrix (`three_way_runner.fill_failures`, through
    `paired`'s `beside`), and the exact program keeps their expected count through its state merge: its expectation
    equals the simulation's mean on a toy where they are common."""
    rules = J.ToyRules(combine_fee=20, billing=21, target=30, mll=52, dll=None, activation_fee=20, funded_mll=52,
                       win_day=1e9, payout_days=99, payout_share=0.5, payout_cap=400, split=1.0, payout_lag=1)
    sch = J.Schedule("rb1dp", tuple(J.Trade(session=sess, decision=600, entry=605, exit=650, exit_reason="target",
                                            g=6, l=8, tick_value=5.0, entry_cost=H3A_COST, x_target=H3A_COST,
                                            x_stop=H3A_STOP) for sess in range(0, 40, 2)))
    p_ = plan(starts=(0,), seed_indices=tuple(range(3000)), horizon=21, block_sessions=40, budget=None)
    recs = R.run(sch, rules, p_)
    beside = R.fill_failures(recs)
    f = recs[0].fill_failures.astype(float)
    assert beside["fill_failures_per_unit"] == pytest.approx(f.mean()) and beside["fill_failures"] > 0
    dp = J.expect(sch, rules, 0, 21, block_sessions=40)
    assert abs(f.mean() - dp["fill_failures"]) < 4 * f.std() / np.sqrt(f.size), (f.mean(), dp["fill_failures"])
    shown = {}
    R.paired(J.Schedule("design", sch.trades), {k: J.Schedule(k, sch.trades) for k in R.BASELINES}, rules,
             plan(starts=(0,), seed_indices=tuple(range(8)), horizon=21, block_sessions=40, budget=None),
             lambda r: r.balance, beside=shown)
    assert set(shown) == {"design", *R.BASELINES} and all("fill_failures_per_unit" in v for v in shown.values())


def test_n2_a_daily_limit_below_a_trades_costs_is_refused() -> None:
    """n-2: a declared daily limit at or below a trade's costs (entry and the larger exit, at the arm's worse fill)
    is refused before any draw -- such a lane could never trade and never fail."""
    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=500, dll=14.0, activation_fee=1, funded_mll=500,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    sch = _rb1_toy(True, h=5)                                          # costs 2.12 + 12.12 = 14.24 > 14
    with pytest.raises(ValueError, match="n-2"):
        J.simulate(sch, rules, 0, (0,), 3, seed=SEED, part=PART, history=0, block_sessions=5)
    with pytest.raises(ValueError, match="n-2"):
        J.expect(sch, rules, 0, 3, block_sessions=5)
    ok = replace(rules, dll=20.0)
    J.check_costs(sch, ok)
    with pytest.raises(ValueError, match="n-2"):
        J.check_costs(sch, ok, J.ArmSpec(worse_ticks=1))              # +1 tick a fill: 14.24 + 10 > 20



def test_h4_the_baselines_alone_equal_their_place_in_a_paired_call() -> None:
    """For H4 (wt/wt-h4 f897cd7): the four baselines alone, on one plan -- the same refusals as `paired` (exactly the
    four, no plant), and each baseline's matrix, its failures at the fill and its keys equal those of a call with a
    design, key for key."""
    design = toy("design", 3, 90, decision=1200)                      # its moments shared with no baseline
    p_ = plan(seed_indices=tuple(range(16)))
    g_p, g_b, g_d = K.KeyGuard(), K.KeyGuard(), K.KeyGuard()
    side_p, side_b = {}, {}
    xs, _ = R.paired(design, baselines(), RULES, p_, R.p_b, guard=g_p, beside=side_p)
    xb, _ = R.baselines_only(baselines(), RULES, p_, R.p_b, guard=g_b, beside=side_b)
    R.run(design, RULES, p_, J.ArmSpec(), g_d)
    assert set(xb) == set(R.BASELINES)
    for name in R.BASELINES:
        assert np.array_equal(xb[name], xs[name]), name
        assert side_b[name] == side_p[name], name
    assert g_b.keys() == g_p.keys() - g_d.keys() and g_b.keys() and g_d.keys()
    with pytest.raises(ValueError, match="exactly"):
        R.baselines_only({k: v for k, v in baselines().items() if k != "p16"}, RULES, p_, R.p_b)
    with pytest.raises(ValueError, match="plant"):
        R.baselines_only(baselines(), RULES, p_, R.p_b, base_arm=J.ArmSpec(plant_eps=0.1))



def test_s_c_the_walk_never_reads_the_realised_exit() -> None:
    """s-c: S1's walk step and steps come from the volatility at the alert and the limit known at the fill, never
    the realised exit. At a fractional limit (90.5 minutes) the realised exit is the next whole minute (91), and the
    volatility 6.72 sits where the two differ in both the step (2 at 90.5, 3 at 91) and the steps: the schedule's are the
    limit's; histories differing only in the realised hold give the same; and the journey's walk outcome does not read
    a trade's realised exit slot."""
    from extended import three_way_redraw as RD

    params = S1.S1Params(n_sessions=3, time_limit=90.5, rate=0.0)
    vol = np.full(3, 6.72)
    def hist(hold):
        day = (S1.Arrival(1000, hold, "A"),)
        return S1.S1History(params, vol, np.zeros(3), {"A": (day, (), ()), "B": ((), (), ())})
    spec = S1.DesignSpec("sc", stream="A", fixed_stop=37, rr=55 / 37, walk_step=1, per_session=1)
    a, b = S1.schedule(spec, hist(500.0)).trades[0], S1.schedule(spec, hist(9000.0)).trades[0]
    assert a.law == "walk" and (a.walk_step, a.walk_n) == (b.walk_step, b.walk_n)
    assert a.exit - a.entry == 91 and (RD.walk_step(6.72, 90.5), RD.walk_step(6.72, 91.0)) == (2, 3)
    assert a.walk_step == 2 and a.walk_n == RD.walk_steps(6.72, 90.5, 2) != RD.walk_steps(6.72, 91.0, 2)
    t1 = J.Trade(session=0, decision=700, entry=705, exit=760, exit_reason="max_hold", g=55, l=37, tick_value=5.0,
                 walk_step=3, walk_n=40)
    t2 = replace(t1, exit=1100)                                         # another realised exit, nothing else changed
    rules = J.ToyRules(combine_fee=1, billing=21, target=1e9, mll=1e6, dll=None, activation_fee=1, funded_mll=1e6,
                       win_day=1e9, payout_days=1, payout_share=0.5, payout_cap=1, split=1, payout_lag=1)
    outs = []
    for t in (t1, t2):
        L = J.fresh(64, rules)
        L.day, L.dead, L.stopped = np.zeros(64), np.zeros(64, bool), np.zeros(64, bool)
        J._trade_mc(L, t, rules, J.ArmSpec(), J.CoinLanes(SEED, PART, 0, 0, range(64), None, False))
        outs.append(L.bal.copy())
    assert np.array_equal(outs[0], outs[1])



def test_minor1_a_flatten_bound_walks_t_is_the_minutes_to_the_flatten() -> None:
    """The red team's diff check MINOR-1: a trade entering less than `time_limit` before 15:10 CT (entry 1305, 25
    minutes to `SESSION_END` under a 90-minute limit) is flatten-bound, and its walk's T is those 25 minutes, for s and
    n alike -- never the time limit."""
    from extended import three_way_redraw as RD

    params = S1.S1Params(n_sessions=2, time_limit=90.0, rate=0.0)
    vol = np.full(2, 6.72)
    day = (S1.Arrival(1300, 9000.0, "A"),)
    hist = S1.S1History(params, vol, np.zeros(2), {"A": (day, ()), "B": ((), ())})
    spec = S1.DesignSpec("flat", stream="A", fixed_stop=37, rr=55 / 37, walk_step=1, per_session=1, latency=5)
    t = S1.schedule(spec, hist).trades[0]
    T = float(S1.SESSION_END - t.entry)
    assert t.exit_reason == "flatten" and t.law == "walk" and T == 25.0 < params.time_limit
    assert (t.walk_step, t.walk_n) == (RD.walk_step(6.72, T), RD.walk_steps(6.72, T, RD.walk_step(6.72, T)))
    s90 = RD.walk_step(6.72, 90.0)
    assert (t.walk_step, t.walk_n) != (s90, RD.walk_steps(6.72, 90.0, s90))


def test_note4_baselines_alone_with_a_design_sharing_a_moment() -> None:
    """The red team's diff check NOTE-4: with a design that shares its moments with a baseline (naive_coin's sessions
    and decision), each baseline's matrix, failures at the fill and beside readings alone still equal its place in the
    paired call, and the paired call's keys are the union of the baselines' and the design's, the shared moments' keys
    in both."""
    design = toy("design", 3, 90, decision=700)                       # naive_coin's moment on every 15th session
    p_ = plan(seed_indices=tuple(range(16)))
    g_p, g_b, g_d = K.KeyGuard(), K.KeyGuard(), K.KeyGuard()
    side_p, side_b = {}, {}
    xs, _ = R.paired(design, baselines(), RULES, p_, R.p_b, guard=g_p, beside=side_p)
    xb, _ = R.baselines_only(baselines(), RULES, p_, R.p_b, guard=g_b, beside=side_b)
    R.run(design, RULES, p_, J.ArmSpec(), g_d)
    for name in R.BASELINES:
        assert np.array_equal(xb[name], xs[name]), name
        assert side_b[name] == side_p[name], name
    assert g_p.keys() == g_b.keys() | g_d.keys()
    assert g_b.keys() & g_d.keys()                                     # the shared moments drew the same keys
