"""The `Protocol` dataclass and the registry of candidates to compare.

A **protocol** is the whole operating policy, not just a trade profile: what you trade on the
Combine, what you trade once funded, when you take money out, how you size, and how many
accounts you run. Stage one compared *profiles*; the charter's second half is a comparison of
*protocols*, because payout policy and account count interact with the edge and with each
other.

The registry seeds T7 with three families:

1. **Stage one's admissible pairs** -- the best pre-registered combinations from
   `vendor/propsim/edge/T5_RESULTS.md` §2a, which are the natural baseline.
2. **The buffer family** -- stage one's exploratory finding that holding a large balance beats
   taking the maximum (propsim D-45). It is a hint, not a settled value: it was chosen after
   seeing results, its grid was coarse, one optimum was still rising at the largest buffer
   tested, and it priced no payout latency, no reinvestment and no per-contract costs.
3. **Fast-payout variants** -- the opposite direction, which stage one could not evaluate at
   all. Under reinvestment, cash taken early is redeployable; that benefit is invisible to a
   metric with no clock. Registering both directions makes T7 a test rather than a
   confirmation of the hint.

Nothing here is a recommendation. These are the arms of a pre-registered comparison.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterator

#: propsim D-36's limits, tier 2 since D-145 (D-151: flagged and modelled, no longer refused); defined once in
#: `propedge.campaign.conduct` and re-exported here for the modules that import them from this one.
from propedge.campaign.conduct import (  # noqa: E402
    FUNDED_DRAWDOWN, MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN, MIN_RR, protocol_findings,
)


class ConductViolation(ValueError):
    """Raised when a protocol or policy breaches a tier-1 conduct rule (D-145, D-151).

    Tier 1 is refused: a protocol that breaches it is not a candidate. Tier-2 conditions (R at or below 1, a funded
    position above half the drawdown) are no longer refused; they are reported by `conduct_flags()` and their
    Responsible Trading Program consequences are applied by the lockstep engine (`propedge.campaign.conduct`).
    """


@dataclass(frozen=True)
class Protocol:
    """One complete operating policy, to be ranked by time-aware return.

    Attributes:
        name: short identifier used in result files and the report.
        combine_rr / combine_risk: the Combine trade profile (R, dollars per trade).
        funded_rr / funded_risk: the funded-account trade profile.
        trades_per_day: trade slots per day, both stages.
        payout_path: "standard" (5 winning days >= $150) or "consistency" (3 trading days,
            best <= 40 % of window net).
        keep_balance: never request a payout that leaves the balance below this. 0 takes the
            maximum allowed as soon as eligible -- the fast-payout end of the range.
        payout_frac: fraction of the maximum allowed request to take.
        sizing_rule: "fixed_dollar" (constant dollar risk) or "fraction_of_balance"
            (risk scales with the account balance).
        max_concurrent_accounts: how many funded accounts this protocol runs at once. Capped
            by the firm's limit of 5 active funded accounts (`max_active_funded_accounts`,
            verified 2026-09-22 from article 8284215, D-21) -- `propedge.campaign.reinvest`
            reads the verified cap at simulation time through the rule gate, which would
            refuse again if the rule ever lost its verified status.
        family: which arm of the comparison this belongs to.
        source: where the parameters came from.
        note: what this arm is testing.
    """

    name: str
    combine_rr: float
    combine_risk: float
    funded_rr: float
    funded_risk: float
    trades_per_day: int = 1
    payout_path: str = "standard"
    keep_balance: float = 0.0
    payout_frac: float = 1.0
    sizing_rule: str = "fixed_dollar"
    max_concurrent_accounts: int = 1
    family: str = ""
    source: str = ""
    note: str = ""
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.check_conduct()

    def check_conduct(self) -> None:
        """Refuse a tier-1 breach (D-151). Raises `ConductViolation`; tier 2 is reported, not refused."""
        tier1, _ = protocol_findings(self)
        if tier1:
            raise ConductViolation(f"protocol {self.name!r}: " + "; ".join(tier1) + " (tier 1, refused)")

    def conduct_flags(self) -> list[str]:
        """Tier-2 conditions this protocol carries (D-145, D-151): allowed, and priced by the engine's conduct
        model. Empty when there are none."""
        return protocol_findings(self)[1]

    # ---------------------------------------------------------------- engine
    def combine_policy(self):
        """A `propsim.Policy` for the Combine leg."""
        from propedge.contract.adapter import Policy

        return Policy(
            rr=self.combine_rr,
            risk=self.combine_risk,
            trades_per_day=self.trades_per_day,
            payout_path=self.payout_path,
        )

    def funded_policy(self):
        """A `propsim.Policy` for the funded leg, carrying the payout policy."""
        from propedge.contract.adapter import keep_balance_policy

        return keep_balance_policy(
            self.funded_rr,
            self.funded_risk,
            self.keep_balance,
            trades_per_day=self.trades_per_day,
            payout_path=self.payout_path,
            payout_frac=self.payout_frac,
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def label(self) -> str:
        buf = f"keep ${self.keep_balance:,.0f}" if self.keep_balance else "take max"
        return (
            f"{self.name}: combine {self.combine_rr}:1 ${self.combine_risk:,.0f} / "
            f"funded {self.funded_rr}:1 ${self.funded_risk:,.0f}, {buf}, "
            f"{self.max_concurrent_accounts} acct"
        )


class ProtocolRegistry:
    """The named protocols available to a comparison."""

    def __init__(self, protocols: dict[str, Protocol] | None = None):
        self._p: dict[str, Protocol] = dict(protocols or {})

    def add(self, protocol: Protocol) -> Protocol:
        if protocol.name in self._p:
            raise ValueError(f"protocol {protocol.name!r} is already registered")
        self._p[protocol.name] = protocol
        return protocol

    def get(self, name: str) -> Protocol:
        try:
            return self._p[name]
        except KeyError:
            raise KeyError(
                f"unknown protocol {name!r}; registered: {', '.join(sorted(self._p))}"
            ) from None

    def family(self, family: str) -> list[Protocol]:
        return [p for p in self._p.values() if p.family == family]

    def all(self) -> list[Protocol]:
        return sorted(self._p.values(), key=lambda p: p.name)

    def __iter__(self) -> Iterator[Protocol]:
        return iter(self.all())

    def __len__(self) -> int:
        return len(self._p)

    def __contains__(self, name: str) -> bool:
        return name in self._p


def _stage_one_pairs() -> list[Protocol]:
    """Best pre-registered admissible pairs from `vendor/propsim/edge/T5_RESULTS.md` §2a.

    Stage one's headline pairs at e = 0.05 (2:1 $750 Combine, 1.5:1 $1,000 funded) and at
    e >= 0.10 (1.5:1 $500 Combine, 1.5:1 $1,000 funded), taking the maximum payout as soon as
    eligible. 1:1 $1,500 is **not** here: stage one marks it "reference, not admissible"
    because R = 1 breaks the first conduct guardrail.
    """
    src = "vendor/propsim/edge/T5_RESULTS.md §2a (pre-registered, take-the-maximum, 1y horizon)"
    return [
        Protocol(
            name="s1_pair_low_edge",
            combine_rr=2.0, combine_risk=750.0,
            funded_rr=1.5, funded_risk=1000.0,
            keep_balance=0.0, family="stage_one_baseline", source=src,
            note="Stage one's best admissible pair at e = 0.05. Baseline arm.",
        ),
        Protocol(
            name="s1_pair_high_edge",
            combine_rr=1.5, combine_risk=500.0,
            funded_rr=1.5, funded_risk=1000.0,
            keep_balance=0.0, family="stage_one_baseline", source=src,
            note="Stage one's best admissible pair at e >= 0.10. Baseline arm.",
        ),
        Protocol(
            name="s1_pair_consistency_path",
            combine_rr=2.0, combine_risk=750.0,
            funded_rr=2.0, funded_risk=750.0,
            payout_path="consistency", keep_balance=0.0,
            family="stage_one_baseline",
            source="vendor/propsim/edge/T5_RESULTS.md §2b",
            note=(
                "Consistency path. Relevant because Responsible Trading Program placement "
                "puts new funded accounts on this path (propsim D-43); stage one measured "
                "values 10-20 % lower."
            ),
        ),
    ]


def _buffer_family() -> list[Protocol]:
    """Stage one's exploratory buffer finding (propsim D-45) as comparison arms.

    Its best found was 1.5:1 at $500 with an $8,000 buffer. **Treated as a hypothesis here**:
    exploratory, coarse grid, one optimum still rising at the largest buffer tested, and no
    payout latency, reinvestment or per-contract costs priced. The whole point of T7 is to
    find out whether it survives a clock.
    """
    src = "vendor/propsim/edge/T5_RESULTS.md §3 (EXPLORATORY, propsim D-44/D-45)"
    out = []
    for buf in (2000.0, 5000.0, 8000.0, 12000.0):
        out.append(
            Protocol(
                name=f"buffer_{int(buf)}",
                combine_rr=1.5, combine_risk=500.0,
                funded_rr=1.5, funded_risk=500.0,
                keep_balance=buf, family="buffer", source=src,
                note=(
                    f"Hold at least ${buf:,.0f} before requesting a payout. Stage one's best "
                    "found was this profile at $8,000, but it priced no latency, no "
                    "reinvestment and no per-contract costs."
                ),
            )
        )
    return out


def _fast_payout_family() -> list[Protocol]:
    """Fast-payout variants -- the direction stage one's metric could not evaluate.

    Taking cash out early costs protection (the funded floor drops to $0 on any payout) but
    buys redeployable capital. Under a static EV metric the first effect is visible and the
    second is not, which is exactly why these arms are registered: to let the comparison
    answer it rather than inherit stage one's answer.
    """
    src = "stage two, registered as the opposite arm to the buffer family (D-02)"
    return [
        Protocol(
            name="fast_take_max",
            combine_rr=1.5, combine_risk=500.0,
            funded_rr=1.5, funded_risk=500.0,
            keep_balance=0.0, payout_frac=1.0,
            family="fast_payout", source=src,
            note="Take the maximum allowed payout as soon as eligible. Fastest cash, least protection.",
        ),
        Protocol(
            name="fast_half",
            combine_rr=1.5, combine_risk=500.0,
            funded_rr=1.5, funded_risk=500.0,
            keep_balance=0.0, payout_frac=0.5,
            family="fast_payout", source=src,
            note="Take half the allowed request: early cash while leaving some cushion.",
        ),
        Protocol(
            name="fast_small_buffer",
            combine_rr=1.5, combine_risk=500.0,
            funded_rr=1.5, funded_risk=500.0,
            keep_balance=1000.0, payout_frac=1.0,
            family="fast_payout", source=src,
            note="A minimal buffer: the smallest hold that still leaves a cushion after a payout.",
        ),
        Protocol(
            name="fast_take_max_5acct",
            combine_rr=1.5, combine_risk=500.0,
            funded_rr=1.5, funded_risk=500.0,
            keep_balance=0.0, payout_frac=1.0,
            max_concurrent_accounts=5,
            family="fast_payout", source=src,
            note=(
                "Fast payouts at the firm's account cap. Tests whether early cash compounds "
                "into more accounts faster than a buffer compounds within one. Requires the "
                "account cap to be verified (T1)."
            ),
        ),
    ]


def default_registry() -> ProtocolRegistry:
    """The protocols T7 compares. Arms of a test, not recommendations."""
    reg = ProtocolRegistry()
    for p in _stage_one_pairs() + _buffer_family() + _fast_payout_family():
        reg.add(p)
    return reg


REGISTRY = default_registry()
