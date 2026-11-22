"""Q-170: the vectorised generator (`extended/three_way_fastkeys.py`) is admitted only because it is bit-identical to the
scalar path (`SeedSequence(key)` + Philox (4x64) + the top 52 bits: `three_way_keys.uniforms`, `triggers.coin_uniform`)
-- no engine, no bar; fast. Seeds: the tests' role seed of H3's block for keys made through `key_matrix`; the law's core
(`raw_outputs`, `seed_state32`) is also checked on raw words, the seed word included, over the whole 32-bit range.

- **10^5 random coin keys** over every field's range (part, history, seed index, start, moment below 2^32; every draw
  kind; the one underlying), and 10^5 random keys of every other kind -- the enforcement tag 6 included: the first four
  raw outputs, the uniforms and their twins equal the scalar path's, key by key;
- **the boundary words** -- every key of nine words, and of eight, each word 0 or 2^32 - 1 (the seed word too, on the
  law's core), and short keys of one to four words (SeedSequence's zero padding);
- **many outputs** -- R-10's walk reads up to dozens a key: the first 37 outputs equal `random_raw(37)`;
- **the key guard's states** equal `three_way_keys.key_state`;
- **the wrappers** -- `coin_uniforms` and `enforce_uniforms` equal `Unit.coin_key` / `enforce_key` read by the scalar path,
  and `triggers.coin_uniform`; `key_matrix` refuses what `seed_key` refuses.
"""
from __future__ import annotations

import itertools

import numpy as np
import pytest

from extended import three_way_fastkeys as F
from extended import three_way_keys as K
from extended import three_way_seeds as S

SEED = S.issue("tests")
TEST_ID = S.TEST_IDS["fastkeys"]
N = 100_000
W = 2 ** 32


def _rng(rep: int) -> np.random.Generator:
    return np.random.default_rng(K.seed_key(SEED, "test", test=TEST_ID, replicate=rep))


def _scalar_raw(M: np.ndarray, n: int) -> np.ndarray:
    return np.array([np.random.Philox(np.random.SeedSequence([int(x) for x in row])).random_raw(n) for row in M],
                    dtype=np.uint64)


#: a seed outside every block, for the `test` kind's whole word range (the tests' seed draws only its declared test
#: ids; the generator's law does not read the seed's provenance)
PLAIN_SEED = 4242


def _key(M: np.ndarray, j: int, kind: str = "coin"):
    """Row j of a block seed's matrix, rebuilt through `seed_key` (a block key is read only as `seed_key` built it)."""
    names = K.KEY_KINDS[kind][1]
    return K.seed_key(SEED, kind, **dict(zip(names, (int(x) for x in M[j][2:]))))


def _fields(rng: np.random.Generator, kind: str, n: int) -> dict[str, np.ndarray]:
    _, names = K.KEY_KINDS[kind]
    f = {nm: rng.integers(0, W, n, dtype=np.int64) for nm in names}
    if kind == "coin":
        f["underlying"] = np.ones(n, np.int64)
        f["draw_kind"] = rng.choice(np.array(list(K.DRAW_KINDS.values())), n)
    return f


def test_1e5_random_coin_keys_every_draw_kind() -> None:
    f = _fields(_rng(0), "coin", N)
    M = F.key_matrix(SEED, "coin", **f)
    raw = F.raw_outputs(M, 4)
    assert np.array_equal(raw, _scalar_raw(M, 4))
    u, ut = F.uniforms(M, 4), F.uniforms(M, 4, twin=True)
    assert np.array_equal(u, K.to_uniform(raw >> np.uint64(12))) and np.all(u + ut == 1.0)
    assert set(np.unique(M[:, 8]).tolist()) == set(K.DRAW_KINDS.values())
    for j in range(0, N, 997):                                         # the scalar wrapper itself, key by key
        assert np.array_equal(u[j], K.uniforms(_key(M, j), 4)) and _key(M, j) == [int(x) for x in M[j]]
        assert np.array_equal(ut[j], K.uniforms(_key(M, j), 4, twin=True))


@pytest.mark.parametrize("kind", ["enforce", "history", "symmetry", "plant", "test"])
def test_1e5_random_keys_of_every_other_kind(kind: str) -> None:
    n = N if kind == "enforce" else N // 10
    M = F.key_matrix(PLAIN_SEED if kind == "test" else SEED, kind,
                     **_fields(_rng(1 + list(K.KEY_KINDS).index(kind)), kind, n))
    assert np.array_equal(F.raw_outputs(M, 1), _scalar_raw(M, 1))
    if kind == "enforce":
        assert int(M[0, 1]) == 6


def test_the_boundary_words() -> None:
    for L in (9, 8):
        M = np.array(list(itertools.product((0, W - 1), repeat=L)), dtype=np.uint64)
        assert np.array_equal(F.raw_outputs(M, 4), _scalar_raw(M, 4))
        assert np.array_equal(F.seed_state32(M, 4),
                              np.array([np.random.SeedSequence([int(x) for x in r]).generate_state(4) for r in M]))
    for L in (1, 2, 3, 4, 5):
        M = np.array(list(itertools.product((0, 1, W - 1), repeat=L)), dtype=np.uint64)
        assert np.array_equal(F.raw_outputs(M, 2), _scalar_raw(M, 2))
    M = F.key_matrix(SEED, "coin", part=W - 1, history=0, seed_index=W - 1, start=0, underlying=1, moment=W - 1,
                     draw_kind=K.WALK)
    assert np.array_equal(F.raw_outputs(M, 1), _scalar_raw(M, 1))


def test_many_outputs_and_the_raw_seed_word() -> None:
    rng = _rng(9)
    M = rng.integers(0, W, (2000, 9), dtype=np.uint64)                # the seed word over its whole range
    assert np.array_equal(F.raw_outputs(M, 37), _scalar_raw(M, 37))


def test_every_output_a_walk_reads() -> None:
    """m-15: the admission compares all n outputs a walk reads, not the first: n up to 1024 steps (S1's longest walks
    at its declared values are below it; `docs/plans/scripts/three_way/h3a_inputs.py` prints them), on walk keys of
    every field's range, against `three_way_keys.uniforms(key, n)` and its twin."""
    f = _fields(_rng(12), "coin", 600)
    f["draw_kind"] = np.full(600, K.WALK)
    M = F.key_matrix(SEED, "coin", **f)
    for n in (5, 64, 1024):
        u = F.uniforms(M, n)
        for j in range(0, 600, 29):
            key = _key(M, j)
            assert np.array_equal(u[j], K.uniforms(key, n)) and np.array_equal(F.uniforms(M[j:j + 1], n, True)[0],
                                                                            K.uniforms(key, n, True))
    assert np.array_equal(F.raw_outputs(M[:200], 1024), _scalar_raw(M[:200], 1024))
    full = _scalar_raw(M[:100], 300)
    for first, n in ((0, 7), (3, 9), (4, 4), (37, 101), (250, 50)):            # any range: the walk's chunks
        assert np.array_equal(F.raw_outputs(M[:100], n, first), full[:, first:first + n]), (first, n)


def test_the_guards_states() -> None:
    M = F.key_matrix(SEED, "coin", **_fields(_rng(10), "coin", 3000))
    st = F.key_states(M)
    for j in range(0, 3000, 7):
        assert tuple(int(x) for x in st[j]) == K.key_state([int(x) for x in M[j]])


def test_the_wrappers_and_the_refusals() -> None:
    from extended import triggers as T

    rng = _rng(11)
    c = rng.integers(0, 1000, 500)
    s = rng.integers(0, 5000, 500)
    m = rng.integers(0, W, 500)
    for dk in K.DRAW_KINDS.values():
        u = F.coin_uniforms(SEED, 30, 2, c, s, m, dk, n=3)
        for j in range(0, 500, 13):
            key = K.Unit(SEED, 30, 2, int(c[j]), int(s[j])).coin_key(int(m[j]), dk)
            assert np.array_equal(u[j], K.uniforms(key, 3))
            assert u[j, 0] == T.coin_uniform(key)
    e = F.enforce_uniforms(SEED, 30, 2, c, s, c % 7, s % 5)
    for j in range(0, 500, 17):
        assert e[j] == K.uniforms(K.Unit(SEED, 30, 2, int(c[j]), int(s[j])).enforce_key(int(c[j] % 7),
                                                                                   int(s[j] % 5)))[0]
    with pytest.raises(ValueError):
        F.key_matrix(SEED, "test", test=[1, W], replicate=0)          # a word of 2^32
    with pytest.raises(ValueError):
        F.key_matrix(SEED, "test", test=[1, -1], replicate=0)
    with pytest.raises(ValueError):
        F.key_matrix(SEED, "test", test=1)                            # a field missing
    with pytest.raises(S.ProvenanceRefused):
        F.key_matrix(int(SEED), "test", test=1, replicate=0)          # the literal, not the issued seed
    with pytest.raises(ValueError):
        F.coin_uniforms(SEED, 1, 0, 0, 0, 0, 9)                      # no such draw kind
    with pytest.raises(S.ProvenanceRefused, match="m-9"):             # a deciding seed in a design-check part
        F.coin_uniforms(S.issue("h3d_coins"), S.PARTS["A1"], 0, 0, 0, 0, K.RACE)
