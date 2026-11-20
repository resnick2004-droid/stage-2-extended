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

**Roles enforced** (m-9): `ROLE_USE` names each role's key kinds and parts, and `three_way_keys.seed_key` refuses a
block seed drawn outside them -- a deciding seed cannot draw in a design-check part, nor a history seed a coin.

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

#: H4's block (the re-baseline's draft, `prereg/DRAFT_H4_rebaseline.md` section 15, wt/wt-h4 f897cd7), kept apart from
#: H3's: its own roles and statuses, issued and role-checked by this module alike; the spares drawn by nothing
H4_ROLES: dict[str, int] = {
    "h4_tests": 20264400,          # the unit tests: H4's T-0 and H4's build (synthetic toys only)
    "h4_0_probe": 20264401,        # H4-0, the probe's synthetic toys (the firm path's cost)
    "h4b_coins": 20264402,         # H4-B: the coin field on the search years -- every baseline, arm and reading
    "h4_spare_3": 20264403,
    "h4_spare_4": 20264404,
    "h4_spare_5": 20264405,
    "h4_spare_6": 20264406,
    "h4_spare_7": 20264407,
    "h4_spare_8": 20264408,
    "h4_spare_9": 20264409,
}
H4_STATUS: dict[str, str] = {role: ("spare, drawn by nothing" if role.startswith("h4_spare") else status)
                             for role, status in (("h4_tests", "tests"), ("h4_0_probe", "design check"),
                                                  ("h4b_coins", "reading"),
                                                  *((r, "") for r in H4_ROLES if r.startswith("h4_spare")))}
H4_BLOCK = frozenset(H4_ROLES.values())
#: every role this module issues, both blocks
_ALL_ROLES: dict[str, int] = {**ROLES, **H4_ROLES}
_ALL_STATUS: dict[str, str] = {**STATUS, **H4_STATUS}

#: the part index every key of a part carries (the note's 1.5: two parts never read one field)
PARTS: dict[str, int] = {"tests": 1, "H3-0": 2, "A1": 3, "A2": 4, "A3": 5, "A4": 6, "D1": 7, "D2": 8, "D3": 9,
                         "H4-0": 10, "H4-B": 11}
#: the `test` key kind's test ids this build's tests use (the note's own test uses id 1, never reused here)
TEST_IDS: dict[str, int] = {"bounds_cover": 11, "power": 12, "history_null": 13, "betting": 14, "s1": 15,
                            "resample": 16, "plant": 17, "mutations": 18, "gate": 19,
                            "fastkeys": 20, "journey_oracle": 21, "walk_oracle": 22, "coverage_tight": 23}


#: m-9 (the red team's read of 746a245): each role's seed draws only its own key kinds in its own parts -- None for the
#: tests' role, which draws anything under the tests' part ids and the `test` kind. A part split into sub-parts keeps
#: its part's id (the sub-parts take disjoint histories or seed indices, so their keys stay distinct).
ROLE_USE: dict[str, tuple[frozenset, frozenset] | None] = {
    "tests": None,
    "h3_0_probe": (frozenset({"history", "coin", "enforce", "plant"}), frozenset({"H3-0"})),
    "h3a_histories": (frozenset({"history", "symmetry", "plant"}), frozenset({"A1", "A2", "A4"})),
    "h3a_coins": (frozenset({"coin", "enforce"}), frozenset({"A1", "A2", "A4"})),
    "h3a3_history_null": (frozenset({"history", "symmetry", "coin", "enforce"}), frozenset({"A3"})),
    "h3d_histories": (frozenset({"history", "symmetry"}), frozenset({"D1", "D2", "D3"})),
    "h3d_coins": (frozenset({"coin", "enforce"}), frozenset({"D1", "D3"})),
    "h3d2_history_null": (frozenset({"symmetry", "coin", "enforce"}), frozenset({"D2"})),
    "h3d3_plants": (frozenset({"plant"}), frozenset({"D3"})),
    "h4_tests": (frozenset({"test", "history", "coin", "enforce"}), frozenset({"H4-0", "H4-B"})),
    "h4_0_probe": (frozenset({"history", "coin", "enforce", "plant"}), frozenset({"H4-0"})),
    "h4b_coins": (frozenset({"coin", "enforce"}), frozenset({"H4-B"})),
}


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
    """The role's seed (H3's block or H4's), carrying its role; refused for an unknown role and for a spare (drawn by
    nothing)."""
    if role not in _ALL_ROLES:
        raise ProvenanceRefused(f"REFUSED: {role!r} is no role of H3's or H4's block")
    if _ALL_STATUS[role].startswith("spare"):
        raise ProvenanceRefused(f"REFUSED: the spare seed {role!r} is drawn by nothing")
    return RoleSeed(_ALL_ROLES[role], role, _ISSUER)


def check_use(seed: "RoleSeed", kind: str, part: int | None) -> None:
    """Refused (`ProvenanceRefused`) when an issued seed would draw a key kind, or a part, outside its role (m-9)."""
    use = ROLE_USE[seed.role]
    if use is None:
        return
    kinds, parts = use
    if kind not in kinds:
        raise ProvenanceRefused(f"REFUSED (m-9): the {seed.role} seed draws {sorted(kinds)} keys, not {kind!r}")
    if kind == "test":                                      # the one kind with no part: its role's kinds decide
        return
    names = {v: k for k, v in PARTS.items()}
    if part is None or names.get(int(part)) not in parts:
        raise ProvenanceRefused(f"REFUSED (m-9): the {seed.role} seed draws in the parts {sorted(parts)}, not "
                                f"{names.get(int(part), part) if part is not None else 'a key with no part'}")


def in_block(seed: int) -> bool:
    """Whether a seed lies in a block this module issues (H3's or H4's): such a seed draws only as an issued
    `RoleSeed`."""
    return int(seed) in BLOCK or int(seed) in H4_BLOCK


def is_issued(seed: object) -> bool:
    """True for a `RoleSeed` this module issued (its value and role agree with the table)."""
    return isinstance(seed, RoleSeed) and _ALL_ROLES.get(getattr(seed, "role", ""), None) == int(seed) \
        and not _ALL_STATUS[seed.role].startswith("spare")


__all__ = ["TESTS", "H3_0", "H3A_HISTORIES", "H3A_COINS", "H3A3_HISTORY_NULL", "H3D_HISTORIES", "H3D_COINS",
           "H3D2_HISTORY_NULL", "H3D3_PLANTS", "SPARE", "ROLES", "STATUS", "BLOCK", "H4_ROLES", "H4_STATUS",
           "H4_BLOCK", "PARTS", "TEST_IDS",
           "ROLE_USE", "ProvenanceRefused", "RoleSeed", "issue", "check_use", "in_block", "is_issued"]
