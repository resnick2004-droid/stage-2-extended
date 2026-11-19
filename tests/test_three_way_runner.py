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
                if L.dead[0] or L.stopped[0] or not J._barrier(t, J._room(L, rules), 0.0)[0] > 0:
                    w *= 1.0 if win else 0.0                    # a trade not taken: one pattern carries the weight
                    continue
                Lt = J._barrier(t, J._room(L, rules), 0.0)
                p = float(Lt[0] / (Lt[0] + t.g))
                w *= p if win else 1 - p
                ch = (t.g * t.tvn - t.x_target) if win else (-Lt[0] * t.tvn - t.x_stop)
                J._settle(L, np.ones(1, bool), np.array([-t.entry_cost + ch]), rules)
            L = J._close(L, k, rules, J.ArmSpec(), budget, None, dp=False)
        total += w * L.ahead[0] / 3.0
        mass += w
    assert abs(mass - 1.0) < 1e-12, mass
    return total


def test_the_rules_by_hand(monkeypatch) -> None:
    """Every outcome forced (the uniforms pinned just above 0, then just below 1): the journey's closes computed by
    hand from the toy rules -- the fee on day 0, a pass at 100 with its activation fee, the funded account's winning
    days, a payout of half the balance after two, its cash a close later; and the losing journey's breaches, each
    replaced by a new evaluation at its close."""
    sch = toy("hand", 1, 12)
    p = plan(starts=(0,), seed_indices=(0,), horizon=9, block_sessions=12, budget=None)
    monkeypatch.setattr(K, "uniforms", lambda key, n=1, twin=False: np.full(n, 2.0 ** -53))
    rec = R.run(sch, RULES, p)[0]
    assert rec.rel[0].tolist() == [-20, -20, -40, -40, -40, 10, 10, 85, 85, 172.5]
    assert rec.first_pass[0] == 2 and rec.first_pay[0] == 5
    assert rec.arrivals[0] == [(5, 50.0), (7, 75.0), (9, 87.5)]
    monkeypatch.setattr(K, "uniforms", lambda key, n=1, twin=False: np.full(n, 1.0 - 2.0 ** -53))
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
    xs, guard = R.paired(design, baselines(), RULES, plan(), R.p_b)
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
    assert sorted(out) == [1, 2] and all(set(v) == {"design", *R.BASELINES} for v in out.values())


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


BAR_MODULES = {"extended.reader", "extended.walker", "extended.triggers", "extended.synthetic_bars",
               "extended.features", "pandas", "propedge"}


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
