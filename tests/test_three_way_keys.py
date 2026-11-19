"""Wave 3.2: the three-way runner's coin field (`extended/three_way_keys.py`, `extended/three_way_seeds.py`) -- no
engine, no bar, no result; fast.

- **the keys are the note's** -- the five kinds equal `three_way_arith.seed_key` field for field, and the coin key
  equals `triggers.coin_key` on the same offer; the uniform equals `triggers.coin_uniform` bit for bit;
- **the antithetic complement is exact** -- u + u' == 1.0 in floating point for every draw, no uniform is one half, and
  the side coin reverses on every key;
- **keys collide nowhere** -- across starts, seeds, moments, draw kinds, parts, histories and the enforcement stream,
  no two keys give one `generate_state`; the coin key carries the start (choice 3) and no account or firm;
- **the refusals** -- a word of 2^32 or more, a missing or extra field, a negative index, a seed of H3's block not
  issued by the seed module (a literal or a derived value), the spare seed; the guard refuses two keys with one state
  (numpy's trailing-zero and split-word traps) and a unit key without its unit's start.
"""
from __future__ import annotations

import importlib.util
import itertools
from pathlib import Path

import numpy as np
import pytest

from extended import three_way_keys as K
from extended import three_way_seeds as S

ROOT = Path(__file__).resolve().parent.parent
ARITH = ROOT / "docs" / "plans" / "scripts" / "three_way" / "three_way_arith.py"
SEED = S.issue("tests")


def _arith():
    spec = importlib.util.spec_from_file_location("three_way_arith_for_keys", ARITH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_five_kinds_are_the_notes() -> None:
    arith = _arith()
    for kind, (tag, names) in arith.KEY_KINDS.items():
        assert K.KEY_KINDS[kind] == (tag, names)
        for vals in itertools.product((0, 1, 7), repeat=len(names)):
            f = dict(zip(names, vals))
            assert K.seed_key(SEED, kind, **f) == arith.seed_key(int(SEED), kind, **f)
    assert K.KEY_KINDS["enforce"][0] not in {t for t, _ in arith.KEY_KINDS.values()}


def test_the_coin_key_and_uniform_are_the_trigger_librarys() -> None:
    from extended import triggers as T

    for session, decision, sub, start, c in itertools.product((0, 5, 900), (930, 1259), (0, 3), (0, 41), (0, 9)):
        off = T.Offer("p16", session, decision, sub, decision - 5, decision, "market")
        unit = T.CoinUnit(int(SEED), 1, 2, c, start)
        u = K.Unit(SEED, 1, 2, c, start)
        mine = u.coin_key(K.moment(session, decision, sub), K.SIDE)
        assert mine == T.coin_key(unit, off)
        assert K.uniforms(mine)[0] == T.coin_uniform(mine)
        assert (1 if K.uniforms(mine)[0] < 0.5 else -1) == T.coin_side(unit, off)


def test_the_antithetic_complement_is_exact() -> None:
    unit = K.Unit(SEED, 1, 0, 3, 17)
    for m, kind in itertools.product(range(0, 4000, 37), (K.SIDE, K.RACE, K.WALK)):
        key = unit.coin_key(m, kind)
        u, ut = K.uniforms(key, 8), K.uniforms(key, 8, twin=True)
        assert np.all(u + ut == 1.0)
        assert np.all(u != 0.5) and np.all((u > 0) & (u < 1))
        assert np.all(np.where(u < 0.5, 1, -1) + np.where(ut < 0.5, 1, -1) == 0)
    i = np.array([0, 1, K.TOP - 1, K.TOP], dtype=np.uint64)
    assert np.array_equal(K.to_uniform(i) + K.to_uniform(i, twin=True), np.ones(4))


def test_keys_collide_nowhere_across_starts_seeds_moments_and_kinds() -> None:
    g = K.KeyGuard()
    n = 0
    for part, hist, c, start in itertools.product((1, 2), (0, 1), range(4), range(5)):
        u = K.Unit(SEED, part, hist, c, start)
        for m, kind in itertools.product((0, 1, K.moment(3, 930, 0), K.moment(3, 930, 1)), K.DRAW_KINDS.values()):
            g.add(u.coin_key(m, kind), start)
            n += 1
        for acct, req in itertools.product(range(2), range(2)):
            g.add(u.enforce_key(acct, req), start)
            n += 1
    assert len(g.states) == n
    coin = set(K.KEY_KINDS["coin"][1])
    assert {"start", "seed_index", "part", "history", "underlying"} <= coin
    assert not coin & {"account", "firm", "instrument"}
    assert {"start", "seed_index"} <= set(K.KEY_KINDS["enforce"][1])
    # under one seed index, two starts read different uniforms at one moment (choice 3)
    a = K.uniforms(K.Unit(SEED, 1, 0, 0, 5).coin_key(77, K.RACE))[0]
    b = K.uniforms(K.Unit(SEED, 1, 0, 0, 6).coin_key(77, K.RACE))[0]
    assert a != b


def test_the_refusals() -> None:
    u = K.Unit(SEED, 1, 0, 0, 0)
    with pytest.raises(ValueError):
        u.coin_key(K.WORD, K.SIDE)                                   # a word of 2^32
    with pytest.raises(ValueError):
        K.seed_key(SEED, "test", test=1)                              # a field missing
    with pytest.raises(ValueError):
        K.seed_key(SEED, "test", test=1, replicate=0, extra=2)        # a field extra
    with pytest.raises(ValueError):
        K.seed_key(SEED, "test", test=-1, replicate=0)
    with pytest.raises(ValueError):
        K.moment(0, 1440, 0)
    with pytest.raises(S.ProvenanceRefused):
        K.seed_key(int(SEED), "test", test=11, replicate=0)           # the literal value, not the issued seed
    with pytest.raises(S.ProvenanceRefused):
        K.seed_key(SEED + 1, "test", test=11, replicate=0)            # a derived value inside the block
    with pytest.raises(S.ProvenanceRefused):
        S.issue("spare")
    with pytest.raises(S.ProvenanceRefused):
        S.RoleSeed(int(SEED), "tests")                                # only issue() makes one
    assert K.seed_key(SEED, "test", test=11, replicate=0)[0] == int(SEED)
    assert S.STATUS.keys() == S.ROLES.keys() and len(S.BLOCK) == 10
    assert sorted(S.BLOCK) == list(range(min(S.BLOCK), min(S.BLOCK) + 10))


def test_the_guard_refuses_the_traps_and_a_key_without_its_start() -> None:
    g = K.KeyGuard()
    g.add([11, 7])
    with pytest.raises(ValueError):
        g.add([11, 7, 0, 0])                                          # the trailing-zero trap
    g2 = K.KeyGuard()
    g2.add([7, 5, 1])
    with pytest.raises(ValueError):
        g2.add([7, 2 ** 32 + 5])                                      # the split-word trap
    u = K.Unit(SEED, 1, 0, 0, 4)
    key = u.coin_key(5, K.RACE)
    with pytest.raises(ValueError):
        K.KeyGuard().add(key, 3)                                      # not its unit's start (N-2)
    with pytest.raises(ValueError):
        K.KeyGuard().add(key)                                         # a unit key added without its start
    assert K.key_start(key) == 4 and K.key_start(u.enforce_key(0, 0)) == 4
    a, b = K.KeyGuard(), K.KeyGuard()
    a.add(key, 4)
    b.add(key, 4)
    with pytest.raises(ValueError):
        K.disjoint(a, b)
    assert K.check_keys([key, u.coin_key(6, K.RACE)]) == 2



def test_m9_each_seed_draws_only_its_role() -> None:
    """The red team's m-9: a deciding seed in a design-check part, a history seed as a coin, a coin seed as a history
    are refused; each role's own use passes; the tests' role is unrestricted."""
    u = dict(history=0, seed_index=0, start=0, underlying=1, moment=0, draw_kind=K.RACE)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(S.issue("h3d_coins"), "coin", part=S.PARTS["A1"], **u)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(S.issue("h3a_histories"), "coin", part=S.PARTS["A1"], **u)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(S.issue("h3a_coins"), "history", part=S.PARTS["A1"], history=0)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(S.issue("h3d3_plants"), "test", test=1, replicate=0)
    K.seed_key(S.issue("h3d_coins"), "coin", part=S.PARTS["D1"], **u)
    K.seed_key(S.issue("h3a_histories"), "history", part=S.PARTS["A2"], history=3)
    K.seed_key(S.issue("h3_0_probe"), "coin", part=S.PARTS["H3-0"], **u)
    assert set(S.ROLE_USE) == set(S.ROLES) - {"spare"}
    used = [p for r, v in S.ROLE_USE.items() if v is not None for p in v[1]]
    assert set(used) <= set(S.PARTS) and "tests" not in used


def test_b2_the_packing_is_injective_and_the_collision_bound_is_stated() -> None:
    assert K.packing_problems() == []
    assert K.collision_bound(2) == pytest.approx(1 / 2 ** 128)
    assert K.collision_bound(10 ** 11) <= (10 ** 11) ** 2 / 2 ** 129
    g = K.KeyGuard.sampled([5, 6], range(200))
    assert g.sample_starts == frozenset({5}) and g.sample_seeds == frozenset(range(K.SAMPLE_SEEDS))
    u = K.Unit(SEED, 1, 0, 100, 6)
    g.add(u.coin_key(3, K.RACE), 6, 100)                              # outside the sample: checked, not stored
    assert g.checked == 1 and not g.states
    with pytest.raises(ValueError, match="N-2"):
        g.add(u.coin_key(3, K.RACE), 5, 100)
