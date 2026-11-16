"""The T7 arms: every protocol the pre-registered comparison will rank (D-119, slice 5).

`k` for a protocol comparison is the number of arms ranked, declared before the run. Here it is
computed from the grid rather than typed, so the pre-registration's table and the run agree by
construction (`tests/test_t7_grid.py`).

The grid, anchored on stage one (D-114):

* **shape** -- the distinct operating policies in `propedge.campaign.protocols.REGISTRY`, taken
  without their dollar risks and account counts: the two legs' R, the payout path, the buffer
  (`keep_balance`) and the request fraction. Stage one's baseline pairs, the buffer family
  (propsim D-45's hint) and the fast-payout family (its opposite) are all here, so the
  comparison is a test and not a confirmation.
* **risk per trade**, set separately for the Combine and the funded account as fractions of the
  verified $2,000 cushion (D-70, D-114): the Combine at 1/8, 1/4, 3/8 and 1/2, which includes
  both baseline pairs ($500 and $750); the funded account at 1/8, 1/4 and 1/2, which includes
  the baseline $1,000. The funded sweep stops at 1/2 because the draft was declared under propsim
  D-36's guardrails, which refused a funded position above half the drawdown and R at or below 1.
  D-145 made those tier 2 (D-151: the engine flags them rather than refusing), but a declared draft
  does not change with a later decision: `t7_admissible` keeps the draft's own rule, so its arm
  count stays what it declared. A draft written after D-145 would state its own.
* **accounts** -- 1, 3 and 5 concurrent funded accounts (the verified cap is 5).

An arm is one point of shape x risks x accounts, deduplicated on its full parameter tuple: two
registry protocols that differ only in a swept parameter are the same arm.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable

from propedge.campaign.protocols import REGISTRY, ConductViolation, Protocol, ProtocolRegistry

COMBINE_RISK_FRACTIONS: tuple[Fraction, ...] = (
    Fraction(1, 8), Fraction(1, 4), Fraction(3, 8), Fraction(1, 2),
)
FUNDED_RISK_FRACTIONS: tuple[Fraction, ...] = (Fraction(1, 8), Fraction(1, 4), Fraction(1, 2))
ACCOUNT_COUNTS: tuple[int, ...] = (1, 3, 5)


@dataclass(frozen=True)
class Shape:
    """A protocol without its swept parameters."""

    combine_rr: float
    funded_rr: float
    payout_path: str
    keep_balance: float
    payout_frac: float
    families: tuple[str, ...]        # registry families this shape appears in
    members: tuple[str, ...]         # registry protocol names with this shape


@dataclass(frozen=True)
class Arm:
    name: str
    shape: Shape
    combine_risk: float
    funded_risk: float
    combine_risk_fraction: Fraction
    funded_risk_fraction: Fraction
    max_concurrent_accounts: int

    def protocol(self) -> Protocol:
        """The arm as a `Protocol`; construction applies the conduct guardrails."""
        s = self.shape
        return Protocol(
            name=self.name,
            combine_rr=s.combine_rr, combine_risk=self.combine_risk,
            funded_rr=s.funded_rr, funded_risk=self.funded_risk,
            payout_path=s.payout_path, keep_balance=s.keep_balance, payout_frac=s.payout_frac,
            max_concurrent_accounts=self.max_concurrent_accounts,
            family="t7_grid", source="propedge.campaign.t7_grid (D-114 sweep over the registry)",
            note=f"shape of {', '.join(s.members)}; risk {self.combine_risk_fraction} / "
                 f"{self.funded_risk_fraction} of the cushion; {self.max_concurrent_accounts} accounts",
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "combine_rr": self.shape.combine_rr, "funded_rr": self.shape.funded_rr,
            "payout_path": self.shape.payout_path, "keep_balance": self.shape.keep_balance,
            "payout_frac": self.shape.payout_frac, "combine_risk": self.combine_risk,
            "funded_risk": self.funded_risk,
            "combine_risk_fraction": str(self.combine_risk_fraction),
            "funded_risk_fraction": str(self.funded_risk_fraction),
            "max_concurrent_accounts": self.max_concurrent_accounts,
            "shape_members": list(self.shape.members),
        }


def t7_admissible(p: Protocol) -> Protocol:
    """The T7 draft's declared admissibility (propsim D-36, kept after D-145 for this draft only): refuse any
    tier-2 condition as well as tier 1. Raises `ConductViolation`."""
    flags = p.conduct_flags()
    if flags:
        raise ConductViolation(f"protocol {p.name!r} is outside the T7 draft's declared guardrails: " + "; ".join(flags))
    return p


def shapes(registry: ProtocolRegistry = REGISTRY) -> list[Shape]:
    """The distinct shapes in the registry, in a stable order."""
    found: dict[tuple, dict[str, list[str]]] = {}
    for p in registry:
        key = (p.combine_rr, p.funded_rr, p.payout_path, p.keep_balance, p.payout_frac)
        rec = found.setdefault(key, {"families": [], "members": []})
        if p.family not in rec["families"]:
            rec["families"].append(p.family)
        rec["members"].append(p.name)
    out = []
    for key, rec in found.items():
        out.append(Shape(
            combine_rr=key[0], funded_rr=key[1], payout_path=key[2], keep_balance=key[3],
            payout_frac=key[4], families=tuple(rec["families"]), members=tuple(sorted(rec["members"])),
        ))
    return sorted(out, key=lambda s: (s.payout_path, s.combine_rr, s.funded_rr, s.keep_balance, -s.payout_frac))


def cushion_from_ledger(ledger: Any | None = None) -> float:
    """The $2,000 cushion both legs' risk fractions are taken of (verified `combine_mll` and
    `xfa_mll_start`, which agree)."""
    if ledger is None:
        from propedge.contract.rules import load_rules

        ledger = load_rules()
    combine = float(ledger.value("combine_mll"))
    funded = abs(float(ledger.value("xfa_mll_start")))
    if combine != funded:
        raise ValueError(f"the Combine MLL ({combine}) and the funded cushion ({funded}) differ")
    return combine


def enumerate_arms(
    registry: ProtocolRegistry = REGISTRY,
    *,
    cushion: float | None = None,
    combine_fractions: Iterable[Fraction] = COMBINE_RISK_FRACTIONS,
    funded_fractions: Iterable[Fraction] = FUNDED_RISK_FRACTIONS,
    account_counts: Iterable[int] = ACCOUNT_COUNTS,
    ledger: Any | None = None,
) -> list[Arm]:
    """Every arm of the comparison, each constructible under the conduct guardrails."""
    cushion = cushion_from_ledger(ledger) if cushion is None else float(cushion)
    arms: list[Arm] = []
    seen: set[tuple] = set()
    for i, s in enumerate(shapes(registry)):
        for fc in combine_fractions:
            for ff in funded_fractions:
                for n in account_counts:
                    key = (s.combine_rr, s.funded_rr, s.payout_path, s.keep_balance, s.payout_frac,
                           float(cushion * fc), float(cushion * ff), int(n))
                    if key in seen:
                        continue
                    seen.add(key)
                    arm = Arm(
                        name=f"arm{len(arms):03d}_s{i}_c{fc.numerator}-{fc.denominator}"
                             f"_f{ff.numerator}-{ff.denominator}_n{n}",
                        shape=s, combine_risk=float(cushion * fc), funded_risk=float(cushion * ff),
                        combine_risk_fraction=Fraction(fc), funded_risk_fraction=Fraction(ff),
                        max_concurrent_accounts=int(n),
                    )
                    t7_admissible(arm.protocol())    # raises ConductViolation if outside the draft's rule
                    arms.append(arm)
    return arms


def k_arms(**kwargs: Any) -> int:
    """`k` for the pre-registration: the number of arms ranked."""
    return len(enumerate_arms(**kwargs))


__all__ = [
    "COMBINE_RISK_FRACTIONS",
    "FUNDED_RISK_FRACTIONS",
    "ACCOUNT_COUNTS",
    "Shape",
    "Arm",
    "shapes",
    "cushion_from_ledger",
    "enumerate_arms",
    "k_arms",
]
