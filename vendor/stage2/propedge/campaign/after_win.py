"""D-390: the operator's two versions after an XFA's big win, as a layer over a state table's policy; D-395: the
speed-first version.

"After the big win" is an XFA whose balance at the session's start is above its starting balance and whose cycle has
fewer than the Standard path's winning days (8284233: five of $150+), the Payout request day excepted: from the winning
trade that first lifts it above the start, and again after each payout. Outside that state the table decides, its
abandon included; inside it:

* **SPEED** -- every trading day the account takes the collect bracket and nothing else: a flip decision at the
  bracket's risk and R, drawn from the collect stream (`FlipMenu`, the engine's flip machinery: copied across the
  accounts in that state, on the side of any position open on another account, its window its own resolution);
* **GROWTH** -- each routed trade the table would take at less than the growth risk is taken at the growth risk, at
  the R the table chose; no bracket.
* **SPEED-FIRST** (D-395) -- SPEED's bracket, but the state lasts until the account can request: after a payout, five
  winning days AND profit since it (8284233); before the first payout always the 2x; after a payout the 2x, the 1x or
  the adaptive choice (`post_payout`); a bracket only where, after its full loss, the room above the floor still
  covers the 1x bracket's full loss -- else the next narrower one that fits, else the table.

Nothing is re-solved: the base table's decisions are read as they are and only the decision returned in that state
changes. The conduct checks read the brackets' leaves beside the table's (a stop wider than the target, or a target no
larger than the stop: tier 2).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from propedge.campaign.risk_policy import PHASES, Decision, Leaf, RiskPolicy

SPEED, GROWTH, SPEED_FIRST = "speed", "growth", "speed_first"
MODES = (SPEED, GROWTH, SPEED_FIRST)
POST_PAYOUT = ("2x", "1x", "adaptive")
EPS = 1e-9
CENT = 0.005                         # the profit since the payout must be at least $0.01 (8284233), read in cents


def brackets_of(menu: Any, cap: float = 500.0) -> tuple[tuple[str, float, float, float], ...]:
    """D-395: the collect menu's brackets the $500 cap in profit allows, widest first, each as (name, risk, R, full
    loss): the name its stop as a multiple of the narrowest's ("1x", "1.5x", "2x"), the full loss its stop at its own
    contracts plus its cost."""
    specs = sorted((s for s in getattr(menu, "specs", (menu,)) if float(s.risk) <= float(cap) + EPS),
                   key=lambda s: float(s.risk))
    if not specs:
        raise ValueError("no collect bracket within the cap (D-395)")
    low = float(specs[0].risk)
    out = []
    for s in reversed(specs):
        realised = s.contracts(float(s.risk)) * float(s.risk_per_contract)
        out.append((f"{float(s.risk) / low:g}x", float(s.risk), float(s.rr), float(realised * (1.0 + float(s.cost_r)))))
    return tuple(out)


@dataclass(frozen=True)
class AfterWinPolicy(RiskPolicy):
    """`base`'s decisions, with D-390's (or D-395's) rule in the after-win state (see the module)."""

    base: Any = None
    mode: str = SPEED
    flip_risk: float = 400.0          # SPEED: the collect bracket's risk and R (D-390 (3): 2x a $200 target)
    flip_rr: float = 0.5
    growth_risk: float = 500.0        # GROWTH: the routed trade's risk (D-390 (4): the $500 cap in profit)
    winning_days: int = 5             # the Standard path's winning days (8284233)
    post_payout: str = "2x"           # SPEED-FIRST: the bracket after a payout (D-395 (4))
    brackets: tuple = ()              # SPEED-FIRST: (name, risk, R, full loss), widest first (`brackets_of`)

    def __post_init__(self) -> None:
        if not isinstance(self.base, RiskPolicy):
            raise ValueError("an after-win policy lays its rule over a state table's policy (D-390)")
        if self.mode not in MODES:
            raise ValueError(f"the after-win mode is one of {MODES} (D-390, D-395)")
        if not (self.flip_risk > 0 and self.flip_rr > 0 and self.growth_risk > 0 and self.winning_days > 0):
            raise ValueError("the bracket's risk and R, the growth risk and the winning days are positive (D-390)")
        if self.mode == SPEED_FIRST:
            if self.post_payout not in POST_PAYOUT:
                raise ValueError(f"the bracket after a payout is one of {POST_PAYOUT} (D-395)")
            names = [b[0] for b in self.brackets]
            if "1x" not in names or "2x" not in names:
                raise ValueError("the speed-first layer needs the 1x and the 2x collect brackets (D-395)")
            object.__setattr__(self, "brackets", tuple((str(n), float(r), float(rr), float(loss))
                                                       for n, r, rr, loss in self.brackets))

    @staticmethod
    def suffix(mode: str, post_payout: str = "2x") -> str:
        return f"+after_win_{mode}" + (f"_{post_payout}" if mode == SPEED_FIRST else "")

    @classmethod
    def over(cls, base: RiskPolicy, mode: str, **kw: Any) -> "AfterWinPolicy":
        what = mode if mode != SPEED_FIRST else f"speed first, after a payout {kw.get('post_payout', '2x')}"
        return cls(id=f"{base.id}{cls.suffix(mode, kw.get('post_payout', '2x'))}", root=base.root, version=base.version,
                   description=f"{base.description} -- D-390: after the big win, {what}", base=base, mode=mode, **kw)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AfterWinPolicy":
        """D-392: the policy `as_dict()` wrote -- the table under it and the layer's settings -- so a replay (the
        Studio's `RiskPolicy.from_dict`) runs the layer, not the table alone."""
        aw = dict(d["after_win"])
        mode = str(aw["mode"])
        post = str(aw.get("post_payout", "2x"))
        pid = str(d["id"])
        suffix = cls.suffix(mode, post)
        if not pid.endswith(suffix):
            raise ValueError(f"an after-win policy's id ends with {suffix!r} (D-392): {pid!r}")
        base = RiskPolicy.from_dict({**{k: v for k, v in d.items() if k != "after_win"}, "id": pid[: -len(suffix)]})
        extra = ({"post_payout": post, "brackets": tuple(tuple(b) for b in aw["brackets"])} if mode == SPEED_FIRST else {})
        p = cls.over(base, mode, flip_risk=float(aw["flip_risk"]), flip_rr=float(aw["flip_rr"]),
                     growth_risk=float(aw["growth_risk"]), winning_days=int(aw["winning_days"]), **extra)
        p.validate()
        return p

    def applies(self, state: dict[str, Any]) -> bool:
        """The after-win state: a funded or paid account above its start, short of its winning days, not the request
        day. SPEED-FIRST (D-395 (2)): short of what the next request needs -- the winning days, and after a payout the
        profit since it too."""
        if not (state.get("phase") in ("funded", "paid") and float(state.get("balance", 0.0)) > EPS
                and not int(state.get("request_day", 0))):
            return False
        short = int(state.get("win_days", 0)) < int(self.winning_days)
        if self.mode == SPEED_FIRST and state.get("phase") == "paid":
            return short or float(state.get("line_gap", 0.0)) < CENT
        return short

    def pick(self, state: dict[str, Any]) -> tuple[str, float, float, float] | None:
        """SPEED-FIRST: the bracket for the state -- the preferred one (D-395 (4)), else the next narrower one the room
        allows (D-395 (3)); None when none fits."""
        by = {b[0]: b for b in self.brackets}
        if state.get("phase") != "paid" or self.post_payout == "2x":
            want = "2x"
        elif self.post_payout == "1x":
            want = "1x"
        else:
            want = "2x" if float(state.get("line_gap", 0.0)) >= by["2x"][3] - EPS else "1x"
        room = float(state.get("cushion", 0.0))
        keep = by["1x"][3]
        names = [b[0] for b in self.brackets]
        for n in names[names.index(want):]:
            if room - by[n][3] >= keep - EPS:
                return by[n]
        return None

    def decide(self, state: dict[str, Any]) -> Decision:
        dec = self.base.decide(state)
        if dec.abandon or not self.applies(state):
            return dec
        if self.mode == SPEED:
            return replace(dec, risk=float(self.flip_risk), rr=float(self.flip_rr), max_trades=1, source="flip",
                           regime=f"{dec.regime} / D-390 after the big win: the collect bracket")
        if self.mode == SPEED_FIRST:
            b = self.pick(state)
            if b is None:
                return dec
            return replace(dec, risk=b[1], rr=b[2], max_trades=1, source="flip",
                           regime=f"{dec.regime} / D-395 speed first: the {b[0]} collect bracket")
        if dec.source == "strategy" and 0.0 < float(dec.risk) < float(self.growth_risk) - EPS:
            return replace(dec, risk=float(self.growth_risk),
                           regime=f"{dec.regime} / D-390 after the big win: ${self.growth_risk:,.0f}")
        return dec

    def bracket_leaf(self) -> Leaf:
        return Leaf("D-390 after-win collect bracket", risk=float(self.flip_risk), rr=float(self.flip_rr), max_trades=1,
                    source="flip")

    def _leaves(self):
        out = list(self.root.leaves(frozenset(PHASES)))
        if self.mode == SPEED:
            out.append((self.bracket_leaf(), frozenset({"funded", "paid"})))
        if self.mode == SPEED_FIRST:
            out.extend((Leaf(f"D-395 speed-first {n} collect bracket", risk=r, rr=rr, max_trades=1, source="flip"),
                        frozenset({"funded", "paid"})) for n, r, rr, _ in self.brackets)
        return out

    def validate(self) -> None:
        from propedge.campaign.conduct import policy_findings
        from propedge.campaign.protocols import ConductViolation

        tier1, _ = policy_findings(self._leaves(), self.id)
        if tier1:
            raise ConductViolation("; ".join(tier1) + " (tier 1, refused)")

    def conduct_flags(self) -> list[str]:
        from propedge.campaign.conduct import policy_findings

        return policy_findings(self._leaves(), self.id)[1]

    def as_dict(self) -> dict[str, Any]:
        aw = {"mode": self.mode, "flip_risk": self.flip_risk, "flip_rr": self.flip_rr, "growth_risk": self.growth_risk,
              "winning_days": self.winning_days}
        if self.mode == SPEED_FIRST:
            aw.update(post_payout=self.post_payout, brackets=[list(b) for b in self.brackets])
        return {**self.base.as_dict(), "id": self.id, "after_win": aw}


__all__ = ["SPEED", "GROWTH", "SPEED_FIRST", "MODES", "POST_PAYOUT", "AfterWinPolicy", "brackets_of"]
