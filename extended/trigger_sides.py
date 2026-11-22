"""The trigger's own side, per source (CHARTER 3.5's side rule; E-221, the operator's O-4 ruling; the lead's R-1 ruling
on Wave 3.5): the side the playbook offers a user, computed from the component's own trigger and never from the coin.

    from extended import trigger_sides as TS
    TS.check_rule(trigger, rule)                      # the declared rule, refused outside the closed vocabulary
    side = TS.trigger_side(trigger, rule, offer)      # -> TriggerSide (typed provenance), or SideRefused

**Why typed.** In the evaluation every side is the coin's (`triggers.coin_side`; `components._trade_row` stamps every
scheduled trade `side_source="coin"`, RL3's fade or break included, since the coin picks the ticket). A string label on
a trade can be relabelled; a `TriggerSide` cannot be made except here (a hand-built one refuses), so a caller holding
one holds a side this function computed from the trigger's own information.

**The rules, a closed vocabulary per source** (`RULES`):

* `p14` -- P-14's breakout: the offer's tag carries the event's sign (`brk<k>+` a close above the previous completed
  reference bar's high, `brk<k>-` below its low; `triggers.P14Breakout.offers`). `with_breakout`: the sign;
  `against_breakout`: its opposite.
* `rl3` -- RL3's tickets: a mapping from each level name of the trigger's kind (`triggers.RL3_SUBS`) to `fade` or
  `break`. The ticket's role (+1 a resistance, above the 08:29 bar's close; -1 a support) and the rule give the side:
  a fade trades against the role (a sell at a resistance), a break with it (a buy above a resistance) --
  `triggers.order_for`'s own pairing, so the order is the library's (a fade limit at the level, a break stop one tick
  beyond).
* `p16` -- none: P-16's marks carry no direction of their own; a P-16 side rule must be declared and built before a
  P-16 component can offer a playbook side.
* `coin` -- never: the coin is the evaluation's device, not the playbook's.

Nothing here reads a bar: the side comes from the offer's tag and role, which the trigger set from bars before its
alert.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from extended import triggers as T

P14_RULES = ("with_breakout", "against_breakout")
RL3_RULES = ("fade", "break")
RULES: dict[str, tuple[str, ...]] = {"p14": P14_RULES, "rl3": RL3_RULES}
NO_SIDE = {
    "p16": "P-16's marks carry no direction of their own: no P-16 side rule is declared or built",
    "coin": "the coin is the evaluation's device, not the playbook's (CHARTER section three point five)",
}
PROVENANCE = "trigger"

_MINT = object()


class SideRefused(ValueError):
    """A side the playbook cannot offer: no declared rule for the source, a rule outside the vocabulary, an offer the
    trigger would not make, or a side not computed here."""


@dataclass(frozen=True)
class TriggerSide:
    """A side computed by `trigger_side` from the trigger's own information: the source, the declared rule (for RL3,
    the level's), the offer's tag, the side (+1 long, -1 short), RL3's ticket rule and the provenance."""

    source: str
    rule: str
    tag: str
    side: int
    ticket_rule: str = ""
    provenance: str = PROVENANCE
    _mint: Any = field(default=None, repr=False, compare=False)

    def _fields(self) -> tuple:
        return self.source, self.rule, self.tag, int(self.side), self.ticket_rule, self.provenance

    def __post_init__(self) -> None:
        # the mint is this module's private object bound to the fields it was made with, so neither a hand-built side
        # nor `dataclasses.replace` of a minted one (a flipped side, another tag) passes
        if not (isinstance(self._mint, tuple) and len(self._mint) == 2 and self._mint[0] is _MINT
                and self._mint[1] == self._fields()):
            raise SideRefused("a trigger side is made only by trigger_side, from the trigger's own information")
        if self.provenance != PROVENANCE or int(self.side) not in (1, -1):
            raise SideRefused("a trigger side is +1 or -1, of the trigger's provenance")


def _minted(source: str, rule: str, tag: str, side: int, ticket_rule: str) -> TriggerSide:
    return TriggerSide(source, rule, tag, side, ticket_rule,
                       _mint=(_MINT, (source, rule, tag, int(side), ticket_rule, PROVENANCE)))


def is_trigger_side(x: Any) -> bool:
    return (isinstance(x, TriggerSide) and isinstance(x._mint, tuple) and x._mint[0] is _MINT
            and x._mint[1] == x._fields())


def _source(trigger: Any) -> str:
    src = getattr(trigger, "source", None)
    if src in NO_SIDE:
        raise SideRefused(f"source {src!r} offers no playbook side: {NO_SIDE[src]}")
    if src not in RULES:
        raise SideRefused(f"source {src!r} is not one of the library's sided sources {sorted(RULES)}")
    return src


def rl3_names(trigger: Any) -> tuple[str, ...]:
    return tuple(n for (k, n) in T.RL3_SUBS if k == trigger.kind)


def check_rule(trigger: Any, rule: Any) -> None:
    """Refuse a declared side rule outside the source's closed vocabulary (`RULES`)."""
    src = _source(trigger)
    if src == "p14":
        if not isinstance(rule, str) or rule not in P14_RULES:
            raise SideRefused(f"P-14's side rule is one of {P14_RULES}, got {rule!r}")
        return
    if not isinstance(rule, Mapping):
        raise SideRefused("RL3's side rule maps each level of its kind to fade or break")
    names = rl3_names(trigger)
    if sorted(rule) != sorted(names):
        raise SideRefused(f"RL3's side rule names exactly the levels {names} of kind {trigger.kind!r}")
    bad = {k: v for k, v in rule.items() if v not in RL3_RULES}
    if bad:
        raise SideRefused(f"RL3's level rules are one of {RL3_RULES}, got {bad!r}")


def trigger_side(trigger: Any, rule: Any, offer: T.Offer) -> TriggerSide:
    """The side of `offer` under the trigger's declared `rule` (the module docstring); refuses otherwise."""
    check_rule(trigger, rule)
    if not isinstance(offer, T.Offer) or offer.source != trigger.source:
        raise SideRefused("the offer is not the trigger's own")
    if trigger.source == "p14":
        stem = f"brk{int(trigger.k)}"
        if offer.tag not in (stem + "+", stem + "-"):
            raise SideRefused(f"P-14's offer tag is {stem}+ or {stem}-, got {offer.tag!r}")
        sign = 1 if offer.tag.endswith("+") else -1
        side = sign if rule == "with_breakout" else -sign
        return _minted("p14", rule, offer.tag, side, "")
    kind, _, name = offer.tag.partition("_")
    if kind != trigger.kind or name not in rule:
        raise SideRefused(f"the ticket {offer.tag!r} is not one of kind {trigger.kind!r}'s levels")
    role = int(offer.role)
    if role not in (1, -1):
        raise SideRefused(f"the ticket {offer.tag!r} has no role (a resistance or a support)")
    how = rule[name]
    side = role if how == "break" else -role
    return _minted("rl3", how, offer.tag, side, how)


__all__ = ["P14_RULES", "RL3_RULES", "RULES", "NO_SIDE", "PROVENANCE", "SideRefused", "TriggerSide",
           "is_trigger_side", "rl3_names", "check_rule", "trigger_side"]
