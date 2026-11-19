"""Wave 3.2: the three-way runner's coin field -- fixed-length keys, the declared generator, the antithetic complement,
and the key guard (`docs/plans/THREE_WAY_TEST_design.md` 1.5, 2.3; choice 3).

**The key** of every draw is `[role seed, kind tag, then exactly the kind's fields]`, every word below 2^32
(`docs/plans/scripts/three_way/three_way_arith.py`'s `seed_key`, whose five kinds keep their tags here; a test holds
the two equal). One kind is added, **`enforce`** (tag 6): the payout-denial stream of the denial ladder, keyed per unit,
account and request and **seeded apart from the coin** -- its tag differs, so no enforcement draw can share a stream
with a side, a race or a walk, and switching the ladder on moves no coin draw (the refusal Wave 3.1 left in
`user_beside.base_problems` came from one path seed driving both in the vendored engine; here they never share a seed).

    coin:    [seed, 3, part, history, seed index, start, underlying, moment, draw kind]   (choice 3: the start in it)
    enforce: [seed, 6, part, history, seed index, start, account, request]

The coin key carries **no account and no firm** (m-9): one user's accounts read one literal draw a moment. The moment
is `(session x 1440 + decision slot) x 16 + sub`, `extended.triggers.moment`'s layout (a test holds `coin_key` equal to
`triggers.coin_key` on the same offer). The draw kinds: `SIDE` 1 (the reflection coin, `triggers.DRAW_SIDE`), `RACE` 2
(the race redraw's one uniform), `WALK` 3 (R-10's stopped walk: one stream, one uniform a step), `MISSED` 4 (measure
28's missed signal).

**The generator, declared** (`extended.triggers`' docstring): numpy's counter-based Philox (4x64) seeded by
`SeedSequence(key)`; the j-th raw 64-bit output's top 52 bits i give the uniform (2 i + 1) 2^-53, on the note's
symmetric grid. **The antithetic twin** reads i' = 2^52 - 1 - i: the uniform 1 - u exactly, in floating point, so
u + u' == 1.0 bit for bit and no uniform is ever exactly one half.

**Refusals.** `seed_key` refuses a missing or extra field, a non-positive seed, a negative field, any word at or above
2^32 (N-8), and a seed of H3's block that `extended.three_way_seeds.issue` did not make (`ProvenanceRefused`). The
`KeyGuard` refuses two different keys with one `generate_state` (2.3; the comparison is what numpy seeds, never the
integers), a coin or enforce key whose start word is not the unit's (N-2), and a disjoint-seed null whose two sets share
a key.

numpy only; reads no file, no bar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np

from extended import three_way_seeds as S

WORD = 2 ** 32
DAY_SLOTS = 1440
MOMENT_SUBS = 16
#: the note's five kinds (tags and fields as `three_way_arith.KEY_KINDS`), and the enforcement stream apart
KEY_KINDS: dict[str, tuple[int, tuple[str, ...]]] = {
    "history": (1, ("part", "history")),
    "symmetry": (2, ("part", "history", "block")),
    "coin": (3, ("part", "history", "seed_index", "start", "underlying", "moment", "draw_kind")),
    "plant": (4, ("part", "history", "plant", "replicate")),
    "test": (5, ("test", "replicate")),
    "enforce": (6, ("part", "history", "seed_index", "start", "account", "request")),
}
#: the kinds whose keys belong to one unit (start, seed index): each must carry the unit's start (N-2)
UNIT_KINDS = ("coin", "enforce")
#: the coin key's draw kinds
SIDE, RACE, WALK, MISSED = 1, 2, 3, 4
DRAW_KINDS = {"side": SIDE, "race": RACE, "walk": WALK, "missed": MISSED}
#: one code per underlying: MNQ and NQ are one (N-4)
UNDERLYING = {"NQ": 1, "MNQ": 1}
#: the symmetric grid: (2 i + 1) 2^-53, i = 0 .. 2^52 - 1
TOP = 2 ** 52 - 1
_SCALE = 2.0 ** -53


def seed_key(seed: int, kind: str, **fields: int) -> list[int]:
    """The fixed-length key of one draw: [seed, tag, the kind's fields in order]; refused as the module says."""
    if kind not in KEY_KINDS:
        raise ValueError(f"unknown key kind {kind!r}")
    tag, names = KEY_KINDS[kind]
    if set(fields) != set(names):
        raise ValueError(f"a {kind} key takes exactly {names}, not {sorted(fields)}")
    vals = [int(fields[n]) for n in names]
    if isinstance(seed, bool) or int(seed) <= 0 or any(v < 0 for v in vals):
        raise ValueError("a seed is positive and every index non-negative")
    if int(seed) >= WORD or any(v >= WORD for v in vals):
        raise ValueError("every word of a key is below 2^32: numpy splits larger integers into words")
    if S.in_block(seed) and not S.is_issued(seed):
        raise S.ProvenanceRefused(f"REFUSED: seed {int(seed)} lies in H3's block but was not issued by "
                                  "extended.three_way_seeds (a literal or a derived value)")
    return [int(seed), tag, *vals]


def key_state(key: Sequence[int], words: int = 4) -> tuple[int, ...]:
    """What numpy seeds from a key: `SeedSequence(key).generate_state(words)`."""
    return tuple(int(x) for x in np.random.SeedSequence([int(k) for k in key]).generate_state(words))


def grid_indices(key: Sequence[int], n: int = 1) -> np.ndarray:
    """The first n grid indices i of the key's stream (the top 52 bits of Philox's raw outputs)."""
    raw = np.random.Philox(np.random.SeedSequence([int(k) for k in key])).random_raw(int(n))
    return np.asarray(raw, dtype=np.uint64) >> np.uint64(12)


def to_uniform(i: np.ndarray, twin: bool = False) -> np.ndarray:
    """(2 i + 1) 2^-53, or its complement (2 (2^52 - 1 - i) + 1) 2^-53 = 1 - u when `twin`; exact in float64."""
    i = np.asarray(i, dtype=np.uint64)
    if twin:
        i = np.uint64(TOP) - i
    return (i.astype(np.float64) * 2.0 + 1.0) * _SCALE


def uniforms(key: Sequence[int], n: int = 1, twin: bool = False) -> np.ndarray:
    """The key's first n uniforms on the symmetric grid (the twin's complements when `twin`)."""
    return to_uniform(grid_indices(key, n), twin)


def moment(session: int, decision: int, sub: int = 0) -> int:
    """The coin key's moment: (session x 1440 + decision slot) x 16 + sub -- a session index and a minute offset."""
    if not (0 <= int(decision) < DAY_SLOTS and 0 <= int(sub) < MOMENT_SUBS and int(session) >= 0):
        raise ValueError("a decision slot is 0 .. 1439, a sub 0 .. 15, a session non-negative")
    m = (int(session) * DAY_SLOTS + int(decision)) * MOMENT_SUBS + int(sub)
    if m >= WORD:
        raise ValueError(f"moment {m} is off the key's grid (every word below 2^32)")
    return m


@dataclass(frozen=True)
class Unit:
    """One user: the coin role seed (a `RoleSeed` of the block, or a seed outside it), the part and history indices,
    the seed's index and the start day. No account, no firm (m-9)."""

    seed: int
    part: int
    history: int
    seed_index: int
    start: int

    def coin_key(self, moment_: int, draw_kind: int, underlying: str = "NQ") -> list[int]:
        if underlying not in UNDERLYING:
            raise ValueError(f"unknown underlying {underlying!r}")
        if draw_kind not in DRAW_KINDS.values():
            raise ValueError(f"unknown draw kind {draw_kind!r}")
        return seed_key(self.seed, "coin", part=self.part, history=self.history, seed_index=self.seed_index,
                        start=self.start, underlying=UNDERLYING[underlying], moment=int(moment_),
                        draw_kind=int(draw_kind))

    def enforce_key(self, account: int, request: int) -> list[int]:
        return seed_key(self.seed, "enforce", part=self.part, history=self.history, seed_index=self.seed_index,
                        start=self.start, account=int(account), request=int(request))


def key_start(key: Sequence[int]) -> int | None:
    """The start word of a unit kind's key (None for another kind)."""
    tag = int(key[1])
    for kind in UNIT_KINDS:
        t, names = KEY_KINDS[kind]
        if tag == t:
            return int(key[2 + names.index("start")])
    return None


@dataclass
class KeyGuard:
    """Every key a run reads, with what numpy seeds from it: refuses two different keys with one state (2.3) and a
    unit key without its unit's start (N-2). The same key read twice (the design and a baseline at one moment on one
    unit: the pairing) is one entry."""

    states: dict[tuple[int, ...], tuple[int, ...]] = field(default_factory=dict)

    def add(self, key: Sequence[int], start: int | None = None) -> None:
        """Record `key`; a unit kind's key (coin, enforce) is added with its unit's `start`, which its start word must
        equal (N-2)."""
        k = tuple(int(x) for x in key)
        ks = key_start(k)
        if ks is not None and (start is None or ks != int(start)):
            raise ValueError(f"REFUSED (N-2): the unit key {k} does not carry its unit's start {start}")
        s = key_state(k)
        prev = self.states.get(s)
        if prev is not None and prev != k:
            raise ValueError(f"REFUSED (2.3): two keys give one generate_state: {prev} and {k}")
        self.states[s] = k

    def keys(self) -> set[tuple[int, ...]]:
        return set(self.states.values())

    def merge(self, other: "KeyGuard") -> None:
        for s, k in other.states.items():
            prev = self.states.get(s)
            if prev is not None and prev != k:
                raise ValueError(f"REFUSED (2.3): two keys give one generate_state: {prev} and {k}")
            self.states[s] = k


def disjoint(a: KeyGuard, b: KeyGuard) -> None:
    """The disjoint-seed null's guard: the two sets share no key and no state (refused otherwise)."""
    shared = set(a.states) & set(b.states)
    if shared:
        raise ValueError(f"REFUSED (2.3): the disjoint seed sets share {len(shared)} key states")


def check_keys(keys: Iterable[Sequence[int]]) -> int:
    """Refuses any two keys of `keys` with one state; returns the number of distinct keys (a unit key checked against
    its own start word)."""
    g = KeyGuard()
    for k in keys:
        g.add(k, key_start(k))
    return len(g.states)


__all__ = ["WORD", "DAY_SLOTS", "MOMENT_SUBS", "KEY_KINDS", "UNIT_KINDS", "SIDE", "RACE", "WALK", "MISSED",
           "DRAW_KINDS", "UNDERLYING", "TOP", "seed_key", "key_state", "grid_indices", "to_uniform", "uniforms",
           "moment", "Unit", "key_start", "KeyGuard", "disjoint", "check_keys"]
