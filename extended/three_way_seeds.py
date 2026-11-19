"""Wave 3.2: H3's seeds -- **the one module the three-way runner reads its seeds from** (the design note's section 7,
`docs/plans/THREE_WAY_TEST_design.md`; the draft declaration `prereg/DRAFT_H3_three_way.md` section 15).

The block is the note's: ten consecutive seeds, one role each, found by the note's search before its first text was
committed and held by `tests/test_three_way_design.py` (the literal scan of every tracked and working text file, and
the arithmetic fold over every tracked `.py`). This file holds the block's literals, so it is one of that test's
`DECLARED_USES` and `DERIVED_USES`; no other code file may hold or build them.

**The run-time guard (the note's section 7, "the guard is the build's run-time assertion").** A seed of the block
enters a key only as a `RoleSeed`, an `int` that only `issue` makes and that carries its role.
`extended.three_way_keys.seed_key` refuses (`ProvenanceRefused`, Q-126's name) any seed of the block that is not a
`RoleSeed` -- a literal typed elsewhere, or a value rebuilt by arithmetic, cannot draw. The spare seed is drawn by
nothing: `issue("spare")` refuses.

**Parts and test ids.** Every coin key carries the part (the note's 1.5), so two parts never read one field even under
one role seed; `PARTS` fixes each part's index. The unit tests share the tests' seed with the note's own test, which
uses the `test` key kind with test id 1; this build's tests take ids from `TEST_IDS`, never 1.

Pure Python; imports nothing.
"""
from __future__ import annotations

#: the block, by role (the note's section 7 table; one role each)
TESTS = 20265870            # the unit tests (the note's and this build's; synthetic toys only)
H3_0 = 20265871             # H3-0, the probe's toys
H3A_HISTORIES = 20265872    # H3-A: the S1 histories of A1 to A4 (the generator's draws; P4's regime signs)
H3A_COINS = 20265873        # H3-A: the coin fields of A1, A2 and A4 (every arm; the disjoint sets by seed index)
H3A3_HISTORY_NULL = 20265874  # H3-A3: the history null's histories, their stream swaps and their pairs' coin fields
H3D_HISTORIES = 20265875    # H3-D: S1 fitted to the search years, and the S2 resamples' block indices
H3D_COINS = 20265876        # H3-D: the coin fields of D1 and D3
H3D2_HISTORY_NULL = 20265877  # H3-D2: the history null's symmetry coins and its pairs' coin fields
H3D3_PLANTS = 20265878      # H3-D3: the plants' own draws (P3's tilts, P4's regime signs)
SPARE = 20265879            # spare, drawn by nothing

ROLES: dict[str, int] = {
    "tests": TESTS,
    "h3_0_probe": H3_0,
    "h3a_histories": H3A_HISTORIES,
    "h3a_coins": H3A_COINS,
    "h3a3_history_null": H3A3_HISTORY_NULL,
    "h3d_histories": H3D_HISTORIES,
    "h3d_coins": H3D_COINS,
    "h3d2_history_null": H3D2_HISTORY_NULL,
    "h3d3_plants": H3D3_PLANTS,
    "spare": SPARE,
}
#: each role's status, as the note's table and the draft's section 15 state it
STATUS: dict[str, str] = {
    "tests": "tests",
    "h3_0_probe": "design check",
    "h3a_histories": "design check",
    "h3a_coins": "design check",
    "h3a3_history_null": "design check",
    "h3d_histories": "deciding",
    "h3d_coins": "deciding",
    "h3d2_history_null": "deciding",
    "h3d3_plants": "deciding",
    "spare": "spare, drawn by nothing",
}
BLOCK = frozenset(ROLES.values())

#: the part index every key of a part carries (the note's 1.5: two parts never read one field)
PARTS: dict[str, int] = {"tests": 1, "H3-0": 2, "A1": 3, "A2": 4, "A3": 5, "A4": 6, "D1": 7, "D2": 8, "D3": 9}
#: the `test` key kind's test ids this build's tests use (the note's own test uses id 1, never reused here)
TEST_IDS: dict[str, int] = {"bounds_cover": 11, "power": 12, "history_null": 13, "betting": 14, "s1": 15,
                            "resample": 16, "plant": 17, "mutations": 18, "gate": 19}


class ProvenanceRefused(RuntimeError):
    """A key would take a seed of the block that this module did not issue, or the spare seed."""


class RoleSeed(int):
    """A seed of the block with its role; made only by `issue`."""

    role: str

    def __new__(cls, value: int, role: str, _token: object = None):
        if _token is not _ISSUER:
            raise ProvenanceRefused("REFUSED: a RoleSeed is made only by extended.three_way_seeds.issue")
        obj = super().__new__(cls, int(value))
        obj.role = role
        return obj

    def __repr__(self) -> str:
        return f"RoleSeed({self.role})"


_ISSUER = object()


def issue(role: str) -> RoleSeed:
    """The role's seed, carrying its role; refused for an unknown role and for the spare (drawn by nothing)."""
    if role not in ROLES:
        raise ProvenanceRefused(f"REFUSED: {role!r} is no role of H3's block ({', '.join(ROLES)})")
    if role == "spare":
        raise ProvenanceRefused("REFUSED: the spare seed is drawn by nothing")
    return RoleSeed(ROLES[role], role, _ISSUER)


def in_block(seed: int) -> bool:
    return int(seed) in BLOCK


def is_issued(seed: object) -> bool:
    """True for a `RoleSeed` this module issued (its value and role agree with the table)."""
    return isinstance(seed, RoleSeed) and ROLES.get(getattr(seed, "role", ""), None) == int(seed) \
        and seed.role != "spare"


__all__ = ["TESTS", "H3_0", "H3A_HISTORIES", "H3A_COINS", "H3A3_HISTORY_NULL", "H3D_HISTORIES", "H3D_COINS",
           "H3D2_HISTORY_NULL", "H3D3_PLANTS", "SPARE", "ROLES", "STATUS", "BLOCK", "PARTS", "TEST_IDS",
           "ProvenanceRefused", "RoleSeed", "issue", "in_block", "is_issued"]
