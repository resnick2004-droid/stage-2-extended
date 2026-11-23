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
            if f.get("part") == 7:
                f["part"] = 70                              # the tests' seed never draws in a run's part (D1 is 7)
            if kind == "test":
                f["test"] = {0: 11, 1: 1, 7: 17}[f["test"]]  # the tests' seed's declared test ids only
            assert K.seed_key(SEED, kind, **f) == arith.seed_key(int(SEED), kind, **f)
    assert K.KEY_KINDS["enforce"][0] not in {t for t, _ in arith.KEY_KINDS.values()}


def test_the_coin_key_and_uniform_are_the_trigger_librarys() -> None:
    from extended import triggers as T

    for session, decision, sub, start, c in itertools.product((0, 5, 900), (930, 1259), (0, 3), (0, 41), (0, 9)):
        off = T.Offer("p16", session, decision, sub, decision - 5, decision, "market")
        unit = T.CoinUnit(SEED, 1, 2, c, start)                       # the issued seed: built through seed_key
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
    for part, hist, c, start in itertools.product((1, 0), (0, 1), range(4), range(5)):     # no run's part
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
    are refused; each role's own use passes; the tests' role draws every kind in the tests' part only (the
    gatekeeper's item 5)."""
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
    issued_h4 = {r for r, st in S.H4_STATUS.items() if not st.startswith("spare")}
    assert set(S.ROLE_USE) == (set(S.ROLES) - {"spare"}) | issued_h4           # H3's roles and H4's issued ones
    used = {r: v[1] for r, v in S.ROLE_USE.items()}
    assert all(v is not None for v in S.ROLE_USE.values())
    assert set().union(*used.values()) <= set(S.PARTS)
    assert [r for r, parts in used.items() if "tests" in parts] == ["tests"] and used["tests"] == {"tests"}
    assert S.ROLE_USE["tests"][0] == S.ALL_KINDS == set(K.KEY_KINDS)


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



def test_h4s_block_and_parts_are_issued_and_role_checked() -> None:
    """For H4 (wt/wt-h4 f897cd7, its section 15): the seed module knows H4's block of ten -- its tests', probe's and
    coin roles issued, its seven spares drawn by nothing -- and the parts H4-0 and H4-B; a literal of the block is
    refused, and each role draws only its kinds in its parts. H3's block and tables are unchanged."""
    assert sorted(S.H4_BLOCK) == list(range(min(S.H4_BLOCK), min(S.H4_BLOCK) + 10))
    assert not S.H4_BLOCK & S.BLOCK and len(S.BLOCK) == 10 and set(S.ROLES) == set(S.STATUS)
    assert {"H4-0", "H4-B", "H4-T"} <= set(S.PARTS) and len(set(S.PARTS.values())) == len(S.PARTS)
    coin = dict(history=0, seed_index=0, start=0, underlying=1, moment=0, draw_kind=K.RACE)
    K.seed_key(S.issue("h4b_coins"), "coin", part=S.PARTS["H4-B"], **coin)
    K.seed_key(S.issue("h4_0_probe"), "coin", part=S.PARTS["H4-0"], **coin)
    K.seed_key(S.issue("h4_tests"), "test", test=1, replicate=0)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(S.issue("h4b_coins"), "coin", part=S.PARTS["H4-0"], **coin)
    with pytest.raises(S.ProvenanceRefused):
        K.seed_key(int(S.issue("h4b_coins")), "coin", part=S.PARTS["H4-B"], **coin)   # the literal, not the issued
    for role, status in S.H4_STATUS.items():
        if status.startswith("spare"):
            with pytest.raises(S.ProvenanceRefused, match="drawn by nothing"):
                S.issue(role)
    assert [S.H4_STATUS[r] for r in ("h4_tests", "h4_0_probe", "h4b_coins", "h4s_schedule_side", "h4_sample")] == [
        "tests", "design check", "reading", "schedule", "audit sample"]
    assert sorted(r for r, st in S.H4_STATUS.items() if st.startswith("spare")) == [f"h4_spare_{i}" for i in range(5, 10)]



def test_minor3_h4s_tests_seed_draws_only_in_its_own_part() -> None:
    """The red team's diff check MINOR-3: the `h4_tests` seed draws its toy keys (history, coin, enforce) only in its
    own part H4-T, and is refused on H4-0's and H4-B's fields -- a tests-seed run of the probe's or the reading's field
    cannot pass the role check; its `test` keys stay allowed."""
    seed = S.issue("h4_tests")
    coin = dict(history=0, seed_index=0, start=0, underlying=1, moment=0, draw_kind=K.RACE)
    enf = dict(history=0, seed_index=0, start=0, account=0, request=0)
    K.seed_key(seed, "coin", part=S.PARTS["H4-T"], **coin)
    K.seed_key(seed, "history", part=S.PARTS["H4-T"], history=0)
    K.seed_key(seed, "enforce", part=S.PARTS["H4-T"], **enf)
    K.seed_key(seed, "test", test=1, replicate=0)
    for part in ("H4-0", "H4-B"):
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(seed, "coin", part=S.PARTS[part], **coin)
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(seed, "history", part=S.PARTS[part], history=0)
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(seed, "enforce", part=S.PARTS[part], **enf)
    for role in ("h4_0_probe", "h4b_coins"):                         # and no other role draws in H4-T
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(S.issue(role), "coin", part=S.PARTS["H4-T"], **coin)
    assert S.PARTS["H4-T"] == 12



def test_h4s_schedule_side_seed_draws_only_coin_keys_in_h4_s() -> None:
    """wt/wt-h4 0727615: the `h4s_schedule_side` seed (once `h4_spare_3`) is the coin's schedule side -- issued for that
    role only, in the block, drawing coin keys in its own part H4-S and nothing else; no other role draws in H4-S; the
    spares 4 to 9 stay refused."""
    seed = S.issue("h4s_schedule_side")
    raw = S.H4_ROLES["h4s_schedule_side"]
    assert int(seed) == raw and seed.role == "h4s_schedule_side" and S.in_block(seed) and S.is_issued(seed)
    assert S.PARTS["H4-S"] == 13 and S.PARTS["H4-T"] == 12
    coin = dict(history=0, seed_index=0, start=0, underlying=1, moment=0, draw_kind=K.SIDE)
    K.seed_key(seed, "coin", part=S.PARTS["H4-S"], **coin)
    for part in ("H4-0", "H4-B", "H4-T"):
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(seed, "coin", part=S.PARTS[part], **coin)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(seed, "enforce", part=S.PARTS["H4-S"], history=0, seed_index=0, start=0, account=0, request=0)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(seed, "test", test=1, replicate=0)
    for role in ("h4_tests", "h4_0_probe", "h4b_coins"):
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(S.issue(role), "coin", part=S.PARTS["H4-S"], **coin)
    with pytest.raises(S.ProvenanceRefused):
        K.seed_key(raw, "coin", part=S.PARTS["H4-S"], **coin)               # the bare int, not the issued seed
    with pytest.raises(S.ProvenanceRefused, match="no role"):
        S.issue("h4_spare_3")                                                # the old spare's name is gone
    for i in range(5, 10):
        with pytest.raises(S.ProvenanceRefused, match="drawn by nothing"):
            S.issue(f"h4_spare_{i}")



def test_gk5_the_tests_seed_draws_in_the_tests_part_only() -> None:
    """The gatekeeper's item 5 on H3: the tests' seed draws every kind in the tests' part and at an index no part
    declares (0, the last word), and the `test` kind; it is refused in every declared run's part, H3-A's, H3-D's and
    H4's included, through `seed_key` and `key_matrix` alike."""
    from extended import three_way_fastkeys as F

    coin = dict(history=0, seed_index=0, start=0, underlying=1, moment=0, draw_kind=K.RACE)
    K.seed_key(SEED, "coin", part=S.PARTS["tests"], **coin)
    K.seed_key(SEED, "plant", part=S.PARTS["tests"], history=0, plant=3, replicate=1)
    K.seed_key(SEED, "test", test=1, replicate=0)
    for free in (0, max(S.PARTS.values()) + 1, 2 ** 32 - 1):
        assert free not in S.PARTS.values()
        K.seed_key(SEED, "coin", part=free, **coin)
    for part in sorted(set(S.PARTS) - {"tests"}):
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(SEED, "coin", part=S.PARTS[part], **coin)
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(SEED, "plant", part=S.PARTS[part], history=0, plant=0, replicate=0)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        F.key_matrix(SEED, "coin", part=np.array([S.PARTS["tests"], S.PARTS["A1"]]), **coin)


def test_gk5_the_field_rules_hold_h4s_h4u_and_the_smaller_j_report() -> None:
    """The lead's ruling on the gatekeeper's item 5: H4-S's schedule side draws only at history 0, seed index 0 and
    start 0; H4's audit sample (`h4_sample`, part H4-U = 14) only at history 0; H3-A's smaller-J report's one key is its
    declared key -- any other value refused, through `seed_key` and `key_matrix` (one bad row refuses the matrix)."""
    from extended import three_way_fastkeys as F
    from extended import three_way_h3a as H

    side = S.issue("h4s_schedule_side")
    ok = dict(history=0, seed_index=0, start=0, underlying=1, moment=7, draw_kind=K.SIDE)
    K.seed_key(side, "coin", part=S.PARTS["H4-S"], **ok)
    F.key_matrix(side, "coin", part=S.PARTS["H4-S"], history=0, seed_index=0, start=0, underlying=1,
                 moment=np.arange(5), draw_kind=K.SIDE)
    for name in ("history", "seed_index", "start"):
        with pytest.raises(S.ProvenanceRefused, match=f"only at {name} = 0"):
            K.seed_key(side, "coin", part=S.PARTS["H4-S"], **{**ok, name: 1})
        with pytest.raises(S.ProvenanceRefused, match=f"only at {name} = 0"):
            F.key_matrix(side, "coin", part=S.PARTS["H4-S"], **{**ok, name: np.array([0, 0, 1])})

    sample = S.issue("h4_sample")
    assert int(sample) == S.H4_ROLES["h4_sample"] and S.PARTS["H4-U"] == 14 and S.H4_STATUS["h4_sample"] == "audit sample"
    K.seed_key(sample, "plant", part=S.PARTS["H4-U"], history=0, plant=11, replicate=5)   # start 11, seed index 5
    with pytest.raises(S.ProvenanceRefused, match="only at history = 0"):
        K.seed_key(sample, "plant", part=S.PARTS["H4-U"], history=1, plant=11, replicate=5)
    for part in ("H4-B", "H4-T", "H4-S", "H4-0"):
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(sample, "plant", part=S.PARTS[part], history=0, plant=0, replicate=0)
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(sample, "coin", part=S.PARTS["H4-U"], **ok)
    for role in ("h4_tests", "h4_0_probe", "h4b_coins", "h4s_schedule_side"):
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            K.seed_key(S.issue(role), "plant", part=S.PARTS["H4-U"], history=0, plant=0, replicate=0)

    rep = S.SMALLER_J_REPORT
    assert (rep["role"], rep["kind"], rep["part"]) == ("h3a_histories", "plant", "A1")
    a, b = H.smaller_j_rng().random(4), H.smaller_j_rng().random(4)
    want = np.random.default_rng(K.seed_key(S.issue("h3a_histories"), "plant", part=S.PARTS["A1"], history=0,
                                            plant=0, replicate=0)).random(4)
    assert np.array_equal(a, b) and np.array_equal(a, want)
    for name in ("history", "plant", "replicate"):
        with pytest.raises(S.ProvenanceRefused, match=f"only at {name} = 0"):
            K.seed_key(S.issue("h3a_histories"), "plant", part=S.PARTS["A1"], **{**rep["fields"], name: 2})
    K.seed_key(S.issue("h3a_histories"), "plant", part=S.PARTS["A4"], history=0, plant=5, replicate=2)  # A4's plants
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(S.issue("h3a_coins"), "plant", part=S.PARTS["A1"], **rep["fields"])



# ------------------------------------------------------------------- the red team's diff check of 805978a


def test_rt1_no_path_builds_or_reads_a_block_key_unchecked() -> None:
    """Finding 1: `triggers.coin_key` builds a block seed's key only through `seed_key` (refused as `seed_key` refuses:
    the schedule side at history 1, seed index 5, start 7; the tests' seed in D1; an unissued block value), with the
    same words as `seed_key` for an issued use; `K.uniforms`, `F.uniforms` and `triggers.coin_uniform` read a block
    seed's key only as `seed_key` / `key_matrix` built it. A plain seed's key is built and read exactly as before."""
    from extended import three_way_fastkeys as F
    from extended import triggers as T

    off = T.Offer("p16", 3, 930, 0, 925, 930, "market")
    side = S.issue("h4s_schedule_side")
    for hist, c, start in ((1, 0, 0), (0, 5, 0), (0, 0, 7), (1, 5, 7)):
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            T.coin_key(T.CoinUnit(side, S.PARTS["H4-S"], hist, c, start), off)
        with pytest.raises(S.ProvenanceRefused, match="m-9"):
            T.coin_side(T.CoinUnit(side, S.PARTS["H4-S"], hist, c, start), off)
    ok = T.CoinUnit(side, S.PARTS["H4-S"], 0, 0, 0)
    key = T.coin_key(ok, off)
    assert key == K.Unit(side, S.PARTS["H4-S"], 0, 0, 0).coin_key(T.moment(off), K.SIDE) and isinstance(key, K.Key)
    assert T.coin_uniform(key) == K.uniforms(key)[0]
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        T.coin_key(T.CoinUnit(SEED, S.PARTS["D1"], 0, 0, 0), off)              # the tests' seed in D1
    with pytest.raises(S.ProvenanceRefused, match="not issued"):
        T.coin_key(T.CoinUnit(int(S.issue("h3d_coins")), S.PARTS["D1"], 0, 0, 0), off)   # an unissued block value
    hand = [int(side), 3, S.PARTS["H4-S"], 1, 5, 7, 1, T.moment(off), K.SIDE]   # a hand-built block key
    for read in (lambda: K.uniforms(hand), lambda: K.grid_indices(hand), lambda: T.coin_uniform(hand),
                 lambda: F.uniforms(np.array([hand], dtype=np.uint64)), lambda: F.raw_outputs(np.array([hand], np.uint64))):
        with pytest.raises(S.ProvenanceRefused, match="no provenance"):
            read()
    plain = T.CoinUnit(12345, 1, 2, 3, 4)                                     # Stage 2's plain seeds: as before
    pk = T.coin_key(plain, off)
    assert type(pk) is list and pk == [12345, T.COIN_TAG, 1, 2, 3, 4, T.UNDERLYING["NQ"], T.moment(off), T.DRAW_SIDE]
    raw = int(np.random.Philox(np.random.SeedSequence(pk)).random_raw())
    assert T.coin_uniform(pk) == (2 * (raw >> 12) + 1) * 2.0 ** -53 == K.uniforms(pk)[0]
    assert F.uniforms(np.array([pk], dtype=np.uint64))[0, 0] == K.uniforms(pk)[0]


def test_rt3_no_run_role_draws_at_an_undeclared_index() -> None:
    """Finding 3 (S1): only the tests' seed may draw at a part index no part declares; every issued run role is refused
    there (0, one past the last part, the last word), through `seed_key`."""
    free = (0, max(S.PARTS.values()) + 1, 2 ** 32 - 1)
    probe = {"history": dict(history=0), "symmetry": dict(history=0, block=0),
             "coin": dict(history=0, seed_index=0, start=0, underlying=1, moment=0, draw_kind=K.SIDE),
             "plant": dict(history=0, plant=0, replicate=0),
             "enforce": dict(history=0, seed_index=0, start=0, account=0, request=0)}
    n = 0
    for role, (kinds, _) in S.ROLE_USE.items():
        if role == "tests":
            continue
        for kind in sorted(kinds - {"test"}):
            for pt in free:
                with pytest.raises(S.ProvenanceRefused, match="m-9"):
                    K.seed_key(S.issue(role), kind, part=pt, **probe[kind])
                n += 1
    assert n >= 3 * (len(S.ROLE_USE) - 1)


def test_rt3_a_field_ruled_use_needs_its_fields() -> None:
    """Finding 3 (S3): a use `FIELD_RULES` fixes is refused when its fields are not given."""
    with pytest.raises(S.ProvenanceRefused, match="no fields were given"):
        S.check_use(S.issue("h4s_schedule_side"), "coin", S.PARTS["H4-S"])
    with pytest.raises(S.ProvenanceRefused, match="no fields were given"):
        S.check_use(S.issue("h4_sample"), "plant", S.PARTS["H4-U"], None)


def test_rt3_a3s_histories_are_a3s_roles_only() -> None:
    """Finding 3 (S11): A3's histories are drawn under A3's own role (the history null's), held in `ROLE_USE`: no other
    role draws a history in A3, and the H3-A histories' role is refused there."""
    with_a3 = [r for r, (kinds, parts) in S.ROLE_USE.items() if "history" in kinds and "A3" in parts]
    assert with_a3 == ["h3a3_history_null"]
    with pytest.raises(S.ProvenanceRefused, match="m-9"):
        K.seed_key(S.issue("h3a_histories"), "history", part=S.PARTS["A3"], history=0)
    K.seed_key(S.issue("h3a3_history_null"), "history", part=S.PARTS["A3"], history=0)


def test_rt4_the_schedule_side_is_a_side_draw_only() -> None:
    """Finding 4: H4-S's rule fixes the draw kind to the side; a race draw under the schedule side is refused."""
    assert S.SIDE_DRAW == K.SIDE and S.FIELD_RULES["h4s_schedule_side"][("coin", "H4-S")]["draw_kind"] == K.SIDE
    u = K.Unit(S.issue("h4s_schedule_side"), S.PARTS["H4-S"], 0, 0, 0)
    u.coin_key(5, K.SIDE)
    for dk in (K.RACE, K.WALK, K.MISSED):
        with pytest.raises(S.ProvenanceRefused, match="only at draw_kind = 1"):
            u.coin_key(5, dk)


def test_rt9_every_field_rule_lies_inside_its_roles_use() -> None:
    """Finding 9: each rule's role issues, its kind and part lie in the role's `ROLE_USE`, every field is its kind's;
    a rule given twice is refused, never silently replaced."""
    for role, rules in S.FIELD_RULES.items():
        kinds, parts = S.ROLE_USE[role]
        S.issue(role)
        for (kind, part), fields in rules.items():
            assert kind in kinds and part in parts, (role, kind, part)
            assert set(fields) <= set(K.KEY_KINDS[kind][1]) - {"part"}, (role, fields)
    assert len(S.FIELD_RULE_ROWS) == sum(len(v) for v in S.FIELD_RULES.values())
    with pytest.raises(ValueError, match="given twice"):
        S.field_rules(S.FIELD_RULE_ROWS + (("h3a_histories", "plant", "A1", {"history": 1}),))


def test_rt2_the_tests_seeds_test_ids_are_declared() -> None:
    """Finding 2: the tests' seed draws the `test` kind only at `TEST_IDS`' ids and the note's own id 1."""
    for tid in (1, *S.TEST_IDS.values()):
        K.seed_key(SEED, "test", test=tid, replicate=0)
    for tid in (0, 2, 99, max(S.TEST_IDS.values()) + 1):
        with pytest.raises(S.ProvenanceRefused, match="test ids"):
            K.seed_key(SEED, "test", test=tid, replicate=0)
