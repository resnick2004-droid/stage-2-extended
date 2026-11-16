"""State-dependent risk policies (D-147).

A risk policy maps an account's state at the start of a session to the per-trade dollar risk
(and, only where the outcome process allows it, the reward multiple R) that the session trades
at. Execution models that step risk down as the cushion to the trailing MLL shrinks, up as the
balance clears a scaling tier, or differently before and after a first payout, are expressed as
a policy; the engine asks it once per account per session and records the answer on every trade.

Three node types, nested freely (the compositional form):

* `Leaf(name, risk, rr=None)` -- trade at `risk` dollars; `rr=None` keeps the outcome process's
  own R. A trade log fixes R when its stop and target were placed, so a log-driven draw refuses
  a leaf that sets R (a different R is a different log); the binary process can honour it.
* `Tiers(on, tiers, name)` -- pick the last tier whose `from` is at or below the state variable
  `on`: `balance`, `cushion` (dollars above the trailing MLL), `cushion_frac` (share of the
  $2,000 MLL), `days_in_state`, or (D-321, funded) `win_days` and `line_gap` (profit since the last
  payout; `NO_LINE` before the first).
* `Phase(combine, funded, paid=None, name)` -- a different node per phase; `paid` is a funded
  account after its first payout (defaults to `funded`).

A `RiskPolicy` wraps a root node with an id, a version and a description, serialises to a plain
dict (saved beside a spec, written into the run manifest) and checks every leaf against D-145's
conduct tiers (`propedge.campaign.conduct`, D-151): positive risk and R are required (tier 1,
refused); R at or below 1 and funded-side risk above half the funded drawdown are tier 2, reported
by `conduct_flags()` and priced by the engine's conduct model.

The decision the engine records: the policy id and version, the regime (the path of node names
that fired, e.g. `funded / cushion >= 1000 / base`), the inputs that selected it, and R and risk.
The contract count is the draw's, recorded beside it on the ledger row.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from propedge.campaign.protocols import (
    FUNDED_DRAWDOWN, MAX_FUNDED_RISK_FRACTION_OF_DRAWDOWN, MIN_RR, ConductViolation,
)

#: D-321: `win_days` (a funded account's Standard-path winning days toward its next payout), `line_gap` (its profit
#: since the last payout -- the balance less the post-payout line; NO_LINE before the first, which is exempt) and
#: `request_day` (1 on the session after a payout request, which 8284233 leaves out of the new cycle), so a funded
#: decision can depend on them as the state table's does
VARIABLES = ("balance", "cushion", "cushion_frac", "days_in_state", "win_days", "line_gap", "request_day")
PHASES = ("combine", "funded", "paid")
SOURCES = ("strategy", "flip", "collect")   # D-339: where a leaf's trade comes from; D-379: collect
MLL = 2000.0
NO_LINE = 1e12


# ------------------------------------------------------------------ nodes


@dataclass(frozen=True)
class Leaf:
    name: str
    risk: float
    rr: float | None = None
    max_trades: int | None = None      # D-162: trades per account per session in this state; None = the protocol's;
                                       # 0 (D-302): no trade in this state -- the account sits, its risk and R unused
    abandon: bool = False              # D-329: end the account at the session's start and free its slot (a Combine
                                       # cancelled, 8284121; an XFA closed at the trader's request, 10657969 / ToU s.8)
    source: str = "strategy"           # D-338/D-339: where the trade comes from -- 'strategy' (a routed signal) or
                                       # 'flip' (the account's scheduled bracket at its slot, every session; funded only)

    def __post_init__(self) -> None:
        if self.max_trades is not None and int(self.max_trades) < 0:
            raise ValueError(f"max_trades must be at least 0 (0: no trade in this state), got {self.max_trades}")
        if self.abandon and (self.max_trades not in (None, 0) or float(self.risk) != 0.0):
            raise ValueError("an abandon leaf trades nothing: risk 0 and max_trades 0 (or unset)")
        if self.source not in SOURCES:
            raise ValueError(f"source is one of {SOURCES}, got {self.source!r}")
        if self.source == "flip" and (self.abandon or self.rr is None or float(self.risk) <= 0.0):
            raise ValueError("a flip leaf is a trade: a positive risk and an R, never abandon")
        if self.source == "collect" and (self.abandon or self.rr is not None or float(self.risk) <= 0.0):
            raise ValueError("a collect leaf is a trade with a take-profit at the shortfall: a positive risk, no R, never "
                             "abandon (D-379)")

    def decide(self, state: dict[str, Any], path: list[str]) -> tuple[list[str], float, float | None]:
        return path + [self.name], float(self.risk), (None if self.rr is None else float(self.rr))

    def leaves(self, phases: frozenset[str]):
        yield self, phases

    def as_dict(self) -> dict[str, Any]:
        d = {"type": "fixed", "name": self.name, "risk": self.risk}
        if self.rr is not None:
            d["rr"] = self.rr
        if self.max_trades is not None:
            d["max_trades"] = int(self.max_trades)
        if self.abandon:
            d["abandon"] = True
        if self.source != "strategy":
            d["source"] = self.source
        return d


@dataclass(frozen=True)
class Tiers:
    on: str
    tiers: tuple[tuple[float, Any], ...]      # (from, node), ascending
    name: str = ""

    def __post_init__(self) -> None:
        if self.on not in VARIABLES:
            raise ValueError(f"tiers must be on one of {VARIABLES}, got {self.on!r}")
        if not self.tiers:
            raise ValueError("a tier table needs at least one tier")
        froms = [float(f) for f, _ in self.tiers]
        if froms != sorted(froms):
            raise ValueError(f"tier thresholds must ascend: {froms}")

    def decide(self, state, path):
        v = float(state[self.on])
        chosen = self.tiers[0]
        for f, node in self.tiers:
            if v >= float(f):
                chosen = (f, node)
        label = (self.name + ": " if self.name else "") + f"{self.on} >= {_fmt(chosen[0], self.on)}"
        return chosen[1].decide(state, path + [label])

    def leaves(self, phases):
        for _, node in self.tiers:
            yield from node.leaves(phases)

    def as_dict(self):
        return {"type": "tiers", "on": self.on, "name": self.name,
                "tiers": [{"from": f, "policy": node.as_dict()} for f, node in self.tiers]}


@dataclass(frozen=True)
class Phase:
    combine: Any
    funded: Any
    paid: Any | None = None
    name: str = ""

    def decide(self, state, path):
        ph = state["phase"]
        node = self.combine if ph == "combine" else (self.paid if ph == "paid" and self.paid is not None else self.funded)
        return node.decide(state, path + [ph])

    def leaves(self, phases):
        yield from self.combine.leaves(frozenset({"combine"}))
        yield from self.funded.leaves(frozenset({"funded"} | ({"paid"} if self.paid is None else set())))
        if self.paid is not None:
            yield from self.paid.leaves(frozenset({"paid"}))

    def as_dict(self):
        d = {"type": "phase", "name": self.name, "combine": self.combine.as_dict(), "funded": self.funded.as_dict()}
        if self.paid is not None:
            d["paid"] = self.paid.as_dict()
        return d


def _fmt(v: float, on: str) -> str:
    if on in ("balance", "cushion", "line_gap"):
        return f"${v:,.0f}"
    if on == "cushion_frac":
        return f"{v:.0%}"
    return f"{v:g}"


def node_from_dict(d: dict[str, Any]):
    t = d.get("type")
    if t == "fixed":
        return Leaf(name=str(d.get("name") or "fixed"), risk=float(d["risk"]),
                    rr=None if d.get("rr") in (None, "") else float(d["rr"]),
                    max_trades=None if d.get("max_trades") in (None, "") else int(d["max_trades"]),
                    abandon=bool(d.get("abandon", False)), source=str(d.get("source") or "strategy"))
    if t == "tiers":
        return Tiers(on=d["on"], name=str(d.get("name") or ""),
                     tiers=tuple((float(x["from"]), node_from_dict(x["policy"])) for x in d["tiers"]))
    if t == "phase":
        return Phase(combine=node_from_dict(d["combine"]), funded=node_from_dict(d["funded"]),
                     paid=node_from_dict(d["paid"]) if d.get("paid") else None, name=str(d.get("name") or ""))
    raise ValueError(f"unknown policy node type {t!r}; expected fixed, tiers or phase")


# ------------------------------------------------------------------ the policy


@dataclass(frozen=True)
class Decision:
    policy_id: str
    policy_version: int
    regime: str
    risk: float
    rr: float | None
    inputs: dict[str, Any] = field(default_factory=dict)
    max_trades: int | None = None      # D-162: the session's trade cap for this account; None = the protocol's
    abandon: bool = False              # D-329: the account ends at the session's start and frees its slot
    source: str = "strategy"           # D-339: 'strategy' (a routed signal) or 'flip' (the account's scheduled bracket)

    def as_row(self) -> dict[str, Any]:
        return {"policy_id": self.policy_id, "policy_version": self.policy_version, "regime": self.regime,
                "policy_risk": self.risk, "policy_rr": self.rr, "policy_max_trades": self.max_trades,
                "policy_abandon": bool(self.abandon), "policy_source": self.source,
                **{"in_" + k: v for k, v in self.inputs.items()}}


@dataclass(frozen=True)
class RiskPolicy:
    id: str
    root: Any
    version: int = 1
    description: str = ""

    def decide(self, state: dict[str, Any]) -> Decision:
        branch = self._branch(state)
        memo = self.__dict__.get("_by_branch")
        if memo is None:
            memo = {}
            object.__setattr__(self, "_by_branch", memo)     # a cache, not a field: equality, repr, as_dict unchanged
        hit = memo.get(branch) if branch is not None else None
        if hit is None:
            path, risk, rr = self.root.decide(state, [])
            leaf = self._leaf_at(state)
            hit = (" / ".join(path), risk, rr, None if leaf.max_trades is None else int(leaf.max_trades),
                   bool(leaf.abandon), str(leaf.source))
            if branch is not None:
                memo[branch] = hit
        inputs = {k: state.get(k) for k in ("phase", "balance", "cushion", "cushion_frac", "days_in_state")}
        for k in ("win_days", "line_gap", "request_day"):  # D-321: recorded where the state carries them
            if k in state:
                inputs[k] = state[k]
        return Decision(self.id, self.version, hit[0], hit[1], hit[2], inputs,
                        max_trades=hit[3], abandon=hit[4], source=hit[5])

    def _branch(self, state: dict[str, Any]) -> tuple | None:
        """R11: the branches the root takes for `state` -- each Phase's phase as read, each Tiers' tier index, the same
        choice `_leaf_at` and the nodes' own `decide` make -- which fix the decision's regime, risk, R, trade limit,
        abandon and source; `decide` builds those once per branch. None (no reuse) when a node on the way is not exactly
        a Leaf, Tiers or Phase, whose own `decide` could read more of the state."""
        from bisect import bisect_right

        cuts = self.__dict__.get("_cuts")
        if cuts is None:
            cuts = {}
            object.__setattr__(self, "_cuts", cuts)
        node, out = self.root, []
        while type(node) is not Leaf:
            if type(node) is Phase:
                ph = state["phase"]
                out.append(ph)
                node = node.combine if ph == "combine" else (node.paid if ph == "paid" and node.paid is not None
                                                              else node.funded)
            elif type(node) is Tiers:
                cut = cuts.get(id(node))
                if cut is None or cut[0] is not node:     # each node's thresholds as floats, read once (node held)
                    froms = tuple(float(f) for f, _ in node.tiers)
                    sortable = all(x == x for x in froms) and all(a <= b for a, b in zip(froms, froms[1:]))
                    cut = cuts[id(node)] = (node, froms, sortable)
                v = float(state[node.on])
                if cut[2] and v == v:
                    # the last tier whose threshold v reaches, else the first: with the thresholds ascending and no
                    # NaN, those are the first `bisect_right` of them -- the loop's choice below, found by halving
                    m = bisect_right(cut[1], v)
                    i = m - 1 if m else 0
                else:
                    i = 0
                    for k, f in enumerate(cut[1]):
                        if v >= f:
                            i = k
                out.append(i)
                node = node.tiers[i][1]
            else:
                return None
        return tuple(out)

    def _leaf_at(self, state: dict[str, Any]) -> Leaf:
        """The leaf the root selects for `state` (the same walk as `decide`)."""
        node = self.root
        while not isinstance(node, Leaf):
            if isinstance(node, Phase):
                ph = state["phase"]
                node = node.combine if ph == "combine" else (node.paid if ph == "paid" and node.paid is not None
                                                              else node.funded)
            else:
                v = float(state[node.on])
                chosen = node.tiers[0][1]
                for f, n in node.tiers:
                    if v >= float(f):
                        chosen = n
                node = chosen
        return node

    def validate(self) -> None:
        """Raise `ConductViolation` if any leaf breaches a tier-1 rule in a phase it can fire in (D-151). Tier-2
        conditions (R at or below 1; a funded leaf above half the drawdown) are reported by `conduct_flags()`."""
        from propedge.campaign.conduct import policy_findings

        tier1, _ = policy_findings(self.root.leaves(frozenset(PHASES)), self.id)
        if tier1:
            raise ConductViolation("; ".join(tier1) + " (tier 1, refused)")

    def conduct_flags(self) -> list[str]:
        """Tier-2 conditions this policy carries (D-145, D-151): allowed, and priced by the engine's conduct model."""
        from propedge.campaign.conduct import policy_findings

        return policy_findings(self.root.leaves(frozenset(PHASES)), self.id)[1]

    def regimes(self) -> list[str]:
        return [leaf.name for leaf, _ in self.root.leaves(frozenset(PHASES))]

    def sets_rr(self) -> bool:
        return any(leaf.rr is not None for leaf, _ in self.root.leaves(frozenset(PHASES)))

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.id, "version": self.version, "description": self.description, "root": self.root.as_dict()}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RiskPolicy":
        if "after_win" in d:                 # D-392: D-390's layer rebuilt whole, never dropped to the table under it
            from propedge.campaign.after_win import AfterWinPolicy

            return AfterWinPolicy.from_dict(d)
        p = cls(id=str(d["id"]), version=int(d.get("version", 1)), description=str(d.get("description", "")),
                root=node_from_dict(d["root"]))
        p.validate()
        return p

    @classmethod
    def from_protocol(cls, protocol: Any, *, with_rr: bool = False) -> "RiskPolicy":
        """The protocol's two fixed legs as a policy: identical to running with no policy."""
        return cls(id=f"fixed:{protocol.name}", description="the protocol's fixed Combine and funded legs",
                   root=Phase(combine=Leaf("combine base", protocol.combine_risk, protocol.combine_rr if with_rr else None),
                              funded=Leaf("funded base", protocol.funded_risk, protocol.funded_rr if with_rr else None)))


def account_state(account: Any, *, kind: str, day: int, mll: float = MLL, cents: bool = False) -> dict[str, Any]:
    """The inputs a policy reads, at the start of `day`'s session, from a lockstep account. `cents` (D-328): the
    dollar inputs -- balance, cushion, the payout-line gap -- rounded to the cent, as the firm's ledger carries them,
    so a floating-point residue from summing the day P&Ls cannot move a balance across a band edge (a path of D-326's
    gate read -$1,000 less two ten-trillionths of a cent as the band below -$1,000); off, the inputs are the floats."""
    money = (lambda x: float(round(float(x) + 0.0, 2))) if cents else float
    balance = money(account.B)
    cushion = money(account.B - account.F)
    win_days, line_gap, request_day = 0, NO_LINE, 0
    if kind == "combine":
        phase, since = "combine", int(getattr(account, "attempt_start_day", account.start_day))
    else:
        paid = account.n_payouts > 0
        phase = "paid" if paid else "funded"
        since = account.start_day + int(account.first_payout_day) + 1 if paid and account.first_payout_day >= 0 else account.start_day
        # D-321: the Standard path's two payout conditions as the account stands -- its winning days toward the next
        # payout and, once paid, its profit since the last payout (8284233: at least $0.01; the first is exempt)
        win_days = int(getattr(account, "win_days", 0))
        line_gap = money(getattr(account, "since_pay", 0.0)) if paid else NO_LINE
        request_day = int(bool(getattr(account, "request_day_next", False)))   # today is the Payout request day
    return {"phase": phase, "balance": balance, "cushion": cushion, "cushion_frac": cushion / mll,
            "days_in_state": max(0, int(day) - int(since)), "day": int(day), "win_days": win_days, "line_gap": line_gap,
            "request_day": request_day}


__all__ = ["VARIABLES", "PHASES", "Leaf", "Tiers", "Phase", "node_from_dict", "Decision", "RiskPolicy", "account_state"]
