"""Q-170: the declared generator's law, vectorised -- **the same uniforms as the scalar path, bit for bit**, for many
keys at once (`extended.three_way_keys.uniforms`, `extended.triggers.coin_uniform`).

**The declared law** (`extended.triggers`' docstring; `three_way_keys`): a key (a list of words, each below 2^32) seeds
numpy's `SeedSequence`; its `generate_state(2, uint64)` is the key of numpy's **Philox (4x64), 10 rounds**, counter
zero; the j-th raw 64-bit output's top 52 bits i give the uniform (2 i + 1) 2^-53, its antithetic twin
(2 (2^52 - 1 - i) + 1) 2^-53. **Nothing of the law changes here**; this module recomputes it on arrays:

* **SeedSequence's hash** (numpy's `_bit_generator.pyx`, fixed-width 32-bit arithmetic): the entropy words hashed into a
  pool of four with `hashmix` (multiplier `MULT_A`, from `INIT_A`), every pool word mixed into every other, every word
  past the fourth mixed into all four, then the output words drawn from the pool cycled with `INIT_B` / `MULT_B`. A key
  of fewer than four words is padded with zeros (`hashmix(0)`), as numpy does.
* **Philox4x64-10** (Salmon et al. 2011, Random123; numpy's `philox.h`): ten rounds of two 64 x 64 -> 128-bit multiplies
  (`mulhilo`, done here on 32-bit halves in uint64) and the key bumped by the Weyl constants between rounds. numpy's
  Philox starts with its four-output buffer empty, so its **first output is the first word of the block at counter
  one**; output j is word j mod 4 of the block at counter 1 + j // 4.

A key matrix holds one key a row, all of one length (each kind's keys have one length: `three_way_keys.KEY_KINDS`).
`key_matrix` builds the rows from field arrays with `seed_key`'s refusals, vectorised: every field given and no other,
every value non-negative and below 2^32, the seed positive and below 2^32, and a seed of H3's block only as a seed the
seed module issued. **Admitted only because `tests/test_three_way_fastkeys.py` holds it bit-identical to the scalar
path** on 10^5 random keys over every field's range, the boundary words 0 and 2^32 - 1, and every draw kind and key kind
(the enforcement tag included).

numpy only; no draw of its own, no file, no bar.
"""
from __future__ import annotations

from typing import Mapping

import numpy as np

from extended import three_way_keys as K
from extended import three_way_seeds as S

U32 = np.uint32
U64 = np.uint64
MASK32 = U64(0xFFFFFFFF)
_S32 = U64(32)

# SeedSequence's constants (numpy/random/bit_generator.pyx)
INIT_A = 0x43B0D7E5
MULT_A = 0x931E8875
INIT_B = 0x8B51F9DD
MULT_B = 0x58F38DED
MIX_MULT_L = 0xCA01F9DD
MIX_MULT_R = 0x4973F715
XSHIFT = 16
POOL = 4

# Philox4x64's constants (Random123; numpy/random/src/philox/philox.h)
PHILOX_M0 = U64(0xD2E7470EE14C6C93)
PHILOX_M1 = U64(0xCA5A826395121157)
PHILOX_W0 = U64(0x9E3779B97F4A7C15)
PHILOX_W1 = U64(0xBB67AE8584CAA73B)
ROUNDS = 10

_SCALE = 2.0 ** -53


# ------------------------------------------------------------------------------------------------ SeedSequence


def _hashmix(value: np.ndarray, h: int) -> tuple[np.ndarray, int]:
    """numpy's hashmix: value ^= h; h *= MULT_A; value *= h; value ^= value >> 16 (all mod 2^32). Returns the value
    and the next hash constant (the constant is the same for every row: it depends only on the call count)."""
    with np.errstate(over="ignore"):
        v = value ^ U32(h)
        h = (h * MULT_A) & 0xFFFFFFFF
        v = v * U32(h)
        v ^= v >> U32(XSHIFT)
    return v, h


def _mix(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore"):
        r = U32(MIX_MULT_L) * x - U32(MIX_MULT_R) * y
        r ^= r >> U32(XSHIFT)
    return r


def seed_state32(keys: np.ndarray, n_words: int) -> np.ndarray:
    """`SeedSequence(row).generate_state(n_words)` (uint32) for every row of `keys` (one key a row, words below
    2^32)."""
    E = np.asarray(keys)
    if E.ndim != 2 or E.shape[1] < 1:
        raise ValueError("keys is one key a row")
    if (E < 0).any() or (E >= K.WORD).any():
        raise ValueError("every word of a key is in [0, 2^32)")
    E = E.astype(U32)
    n, L = E.shape
    zero = np.zeros(n, U32)
    h = INIT_A
    pool = []
    for i in range(POOL):
        v, h = _hashmix(E[:, i] if i < L else zero, h)
        pool.append(v)
    for i_src in range(POOL):
        for i_dst in range(POOL):
            if i_src != i_dst:
                v, h = _hashmix(pool[i_src], h)
                pool[i_dst] = _mix(pool[i_dst], v)
    for i_src in range(POOL, L):
        for i_dst in range(POOL):
            v, h = _hashmix(E[:, i_src], h)
            pool[i_dst] = _mix(pool[i_dst], v)
    out = np.empty((n, int(n_words)), U32)
    hb = INIT_B
    with np.errstate(over="ignore"):
        for j in range(int(n_words)):
            d = pool[j % POOL] ^ U32(hb)
            hb = (hb * MULT_B) & 0xFFFFFFFF
            d = d * U32(hb)
            d ^= d >> U32(XSHIFT)
            out[:, j] = d
    return out


def key_states(keys: np.ndarray, words: int = 4) -> np.ndarray:
    """`three_way_keys.key_state` for every row: what numpy seeds from each key (the key guard's comparison)."""
    return seed_state32(keys, words)


# ------------------------------------------------------------------------------------------------ Philox4x64-10


def _mulhilo(a: np.ndarray, b: U64) -> tuple[np.ndarray, np.ndarray]:
    """(high, low) 64-bit words of the 128-bit product a x b, on 32-bit halves (in place where it can; the caller
    holds numpy's overflow warnings off: every product of two halves fits 64 bits, and the cross sum
    (ll >> 32) + (hl mod 2^32) + lh is at most 2^64 - 1)."""
    b_lo, b_hi = U64(int(b) & 0xFFFFFFFF), U64(int(b) >> 32)
    a_lo = a & MASK32
    a_hi = a >> _S32
    ll = a_lo * b_lo
    hl = a_hi * b_lo
    lh = a_lo * b_hi
    hh = a_hi * b_hi
    t = ll >> _S32
    t += hl & MASK32
    t += lh
    hl >>= _S32
    hh += hl
    t >>= _S32
    hh += t
    return hh, a * b


def philox4x64(ctr: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Philox4x64-10 of counters `ctr` (n x 4 uint64) under keys `key` (n x 2 uint64): the n x 4 output block."""
    c0, c1, c2, c3 = (ctr[:, i].astype(U64) for i in range(4))
    k0, k1 = key[:, 0].astype(U64), key[:, 1].astype(U64)
    with np.errstate(over="ignore"):
        for r in range(ROUNDS):
            if r:
                k0 = k0 + PHILOX_W0
                k1 = k1 + PHILOX_W1
            hi0, lo0 = _mulhilo(c0, PHILOX_M0)
            hi1, lo1 = _mulhilo(c2, PHILOX_M1)
            c0, c1, c2, c3 = hi1 ^ c1 ^ k0, lo1, hi0 ^ c3 ^ k1, lo0
    return np.stack([c0, c1, c2, c3], axis=1)


def raw_outputs(keys: np.ndarray, n: int = 1, first: int = 0) -> np.ndarray:
    """Raw 64-bit outputs first .. first + n - 1 of `Philox(SeedSequence(row))` for every row (n_keys x n uint64):
    output j is word j mod 4 of the block at counter 1 + j // 4 (the generator is counter-based, so any range is read
    directly; `first = 0` is numpy's own stream from its start)."""
    st = seed_state32(keys, 4)
    pk = st.view(U64) if st.flags.c_contiguous else np.ascontiguousarray(st).view(U64)   # generate_state(2, uint64)
    rows = pk.shape[0]
    b0, b1 = int(first) // 4, -(-(int(first) + int(n)) // 4)
    out = np.empty((rows, (b1 - b0) * 4), U64)
    for b in range(b0, b1):
        ctr = np.zeros((rows, 4), U64)
        ctr[:, 0] = U64(b + 1)                    # numpy's buffer starts empty: the first block is at counter one
        out[:, 4 * (b - b0):4 * (b - b0) + 4] = philox4x64(ctr, pk)
    off = int(first) - 4 * b0
    return out[:, off:off + int(n)]


def uniforms(keys: np.ndarray, n: int = 1, twin: bool = False, first: int = 0) -> np.ndarray:
    """`three_way_keys.uniforms(row, first + n, twin)[first:]` for every row of `keys` (n_keys x n float64)."""
    return K.to_uniform(raw_outputs(keys, n, first) >> U64(12), twin)


# ------------------------------------------------------------------------------------------------ key matrices


def key_matrix(seed: int, kind: str, **fields) -> np.ndarray:
    """The rows `three_way_keys.seed_key(seed, kind, **field_i)` for every i, as one uint64 matrix (one key a row):
    each field a scalar or an array (broadcast to a common length); refused as `seed_key` refuses."""
    if kind not in K.KEY_KINDS:
        raise ValueError(f"unknown key kind {kind!r}")
    tag, names = K.KEY_KINDS[kind]
    if set(fields) != set(names):
        raise ValueError(f"a {kind} key takes exactly {names}, not {sorted(fields)}")
    if isinstance(seed, bool) or int(seed) <= 0 or int(seed) >= K.WORD:
        raise ValueError("a seed is positive and below 2^32")
    if S.in_block(seed) and not S.is_issued(seed):
        raise S.ProvenanceRefused(f"REFUSED: seed {int(seed)} lies in a block of the seed module (H3's or "
                                  f"H4's) but was not issued by "
                                  "extended.three_way_seeds")
    cols = np.broadcast_arrays(*[np.asarray(fields[nm], dtype=np.int64) for nm in names])
    if S.in_block(seed):                                               # m-9: each seed draws only its role
        if "part" in fields:
            part_col = cols[names.index("part")].ravel()
            for pt in np.unique(part_col):
                rows = part_col == pt
                S.check_use(seed, kind, int(pt), {nm: set(np.unique(c.ravel()[rows]).tolist())
                                                  for nm, c in zip(names, cols)})
        else:
            S.check_use(seed, kind, None, {nm: set(np.unique(c).tolist()) for nm, c in zip(names, cols)})
    n = cols[0].size
    M = np.empty((n, 2 + len(names)), np.int64)
    M[:, 0], M[:, 1] = int(seed), tag
    for j, c in enumerate(cols):
        M[:, 2 + j] = c.ravel()
    if (M[:, 2:] < 0).any() or (M[:, 2:] >= K.WORD).any():
        raise ValueError("every index is non-negative and every word below 2^32")
    return M.astype(U64)


def coin_uniforms(seed: int, part: int, history: int, seed_index, start, moment, draw_kind, n: int = 1,
                  twin: bool = False, underlying: str = "NQ", first: int = 0) -> np.ndarray:
    """Many units' coin uniforms at once: the same as `three_way_keys.Unit(seed, part, history, c, s).coin_key(m,
    kind)` read by `three_way_keys.uniforms`, row by row."""
    if underlying not in K.UNDERLYING:
        raise ValueError(f"unknown underlying {underlying!r}")
    dk = np.asarray(draw_kind)
    if not np.isin(dk, list(K.DRAW_KINDS.values())).all():
        raise ValueError("unknown draw kind")
    M = key_matrix(seed, "coin", part=part, history=history, seed_index=seed_index, start=start,
                   underlying=K.UNDERLYING[underlying], moment=moment, draw_kind=dk)
    return uniforms(M, n, twin, first)


def enforce_uniforms(seed: int, part: int, history: int, seed_index, start, account, request,
                     twin: bool = False) -> np.ndarray:
    """Many units' enforcement uniforms (the `enforce` kind, seeded apart from the coin), one a row."""
    M = key_matrix(seed, "enforce", part=part, history=history, seed_index=seed_index, start=start, account=account,
                   request=request)
    return uniforms(M, 1, twin)[:, 0]


__all__ = ["INIT_A", "MULT_A", "INIT_B", "MULT_B", "MIX_MULT_L", "MIX_MULT_R", "PHILOX_M0", "PHILOX_M1", "PHILOX_W0",
           "PHILOX_W1", "ROUNDS", "seed_state32", "key_states", "philox4x64", "raw_outputs", "uniforms",
           "key_matrix", "coin_uniforms", "enforce_uniforms"]
