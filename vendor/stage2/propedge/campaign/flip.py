"""D-338 / D-339 / D-343: the flip stream -- a funded account's scheduled bracket at measured statistics.

The two-stream candidate FV3-G/F separates the trades that make or break an account (the strategy's signals, routed
by the queue) from the trades whose only job is the firm's winning-day rule (8284233: five winning days of $150+ net,
positive net profit since the last payout). A flip is a direction-neutral bracket at a scheduled minute, taken every
session the table's state asks for one, and settled from a bracket study's measured shares -- at the target, at the
stop, still open at the flatten (a full loss, NQB1's rule) or, for a time-boxed bracket (D-343), SCRATCHED at the box's
close with the scratches' mean P&L -- and its cost. It claims no edge: its net edge is whatever the shares say
(negative), and the table prices it against the strategy's actions by value (`state_policy.Menu.flip`). Its direction
is the day's shared seeded direction, or the side of any position open on another account at its slot (the firm's
cross-account rule, D-336 (iv)); the outcome draw does not depend on it.

D-343: the operator's two changes. The bracket must resolve within minutes -- a small width in one NQ mini, read for a
box of minutes, scratched when unresolved -- and the flip-state accounts are COPIED: `copy` gives every account the same
outcome on the same calendar day (one shared seed; the draw is keyed by the day, so the order of calls does not matter),
as a trader placing the same bracket at the same minute on every flip-state account would get. Without `copy` each
account's draw is its own, still keyed by the day.

Modelling limits, stated: a flip's window for the cross-account rule is the box (or the slot's mean minutes to
resolution for an un-boxed bracket), not its own exit, which the shares do not time; a scratch's P&L is the scratches'
mean, not a draw from their spread.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Any

import numpy as np

#: the engine's clock: a slot is minutes since the trading day began at 17:00 CT (the resolution and flip maps' convention)
DAY_START_CT = (17, 0)


def slot_from_ct(ct: str) -> int:
    """The engine's slot (minutes since 17:00 CT) of a clock label "HH:MM" CT: "17:00" is 0, "08:30" is 930, "09:00" is
    960. D-345 (7): the flip maps' `decision_slot` is the KIT's unit -- the minute kit's is this clock, the seconds kit's
    is a second offset from its window's start -- so the engine takes a map row's slot from its clock label and checks
    the row's own minute-clock column against it, never the raw `decision_slot`."""
    hh, mm = str(ct).strip().split(":")
    h, m = int(hh), int(mm)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"not a clock label HH:MM: {ct!r}")
    return (h * 60 + m - (DAY_START_CT[0] * 60 + DAY_START_CT[1])) % 1440


def ct_of_slot(slot: int) -> str:
    """The clock label "HH:MM" CT of an engine slot (the inverse of `slot_from_ct`)."""
    s = int(slot)
    if not 0 <= s < 1440:
        raise ValueError(f"a slot is 0 to 1439 minutes after 17:00 CT, got {slot}")
    t = (s + DAY_START_CT[0] * 60 + DAY_START_CT[1]) % 1440
    return f"{t // 60:02d}:{t % 60:02d}"


@dataclass(frozen=True)
class FlipSpec:
    """The flip stream's declared parameters and measured statistics (read from a result file, never typed)."""

    risk: float                      # dollars at risk per flip (the table's flip action)
    rr: float                        # the bracket's R (1.0)
    p_target: float                  # share of brackets at their target
    p_stop: float                    # share at their stop
    p_open: float                    # share still open at the flatten: counted a full loss (an un-boxed bracket)
    cost_r: float                    # cost per attempt in units of the risk (spread, fees, slippage)
    risk_per_contract: float         # dollars one contract risks at the bracket's stop (a micro at $125; a mini at width x $20)
    slots: tuple[int, ...]           # the decision slots, minutes since the trading day began (17:00 CT)
    mean_minutes: float              # the bracket's mean time to resolution: the window's length for the rule
    edge: float                      # the net edge the shares imply, for the record
    edge_lower_bound: float = float("nan")   # its one-sided 95 % bound over yearly blocks, for the lower-bound arm
    source: str = ""                 # the result file the statistics came from
    minutes_by_slot: tuple[float, ...] | None = None   # each slot's own mean minutes to resolution (aligned with `slots`);
    #                                                    None: `mean_minutes` at every slot
    p_scratch: float = 0.0           # D-343: share closed at the box unresolved (a time-boxed bracket); no winning day
    scratch_mean_r: float = 0.0      # D-343: the scratches' mean P&L in units of the risk (their exit tick included)
    box_minutes: float | None = None # D-343: the box; with it the window for the rule is the box at every slot
    copy: bool = False               # D-343: one shared outcome a day across the flip-state accounts
    slot_ct: str = ""                # the slot's clock time, for the record

    def __post_init__(self) -> None:
        if self.risk <= 0 or self.rr <= 0 or self.risk_per_contract <= 0:
            raise ValueError("a flip needs a positive risk, R and risk per contract")
        if not self.slots:
            raise ValueError("a flip needs at least one decision slot")
        tot = self.p_target + self.p_stop + self.p_open + self.p_scratch
        if min(self.p_target, self.p_stop, self.p_open, self.p_scratch) < 0 or abs(tot - 1.0) > 1e-6:
            raise ValueError(f"the flip's shares must be non-negative and sum to one, got {tot:.6f}")
        if self.minutes_by_slot is not None:
            if len(self.minutes_by_slot) != len(self.slots):
                raise ValueError("minutes_by_slot must give one window per decision slot")
            if min(self.minutes_by_slot) <= 0:
                raise ValueError("a slot's window must be positive minutes")
        if self.box_minutes is not None and self.box_minutes <= 0:
            raise ValueError("the box is a positive number of minutes")

    @property
    def net_edge(self) -> float:
        """The shares' net edge per attempt: a target pays R, a stop or an open bracket costs 1, a scratch pays its
        mean, less the cost."""
        return self.p_target * self.rr - (self.p_stop + self.p_open) + self.p_scratch * self.scratch_mean_r - self.cost_r

    def shifted(self, edge: float) -> "FlipSpec":
        """The spec with its target share moved so the net edge is `edge` (the lower-bound arm): the shift goes from
        the target share to the stop share, the open and scratch shares untouched; the shares stay in [0, 1]."""
        fixed = self.p_open + self.p_scratch
        d = (float(edge) - self.net_edge) / (1.0 + self.rr)
        pt = min(max(self.p_target + d, 0.0), 1.0 - fixed)
        return replace(self, p_target=pt, p_stop=1.0 - fixed - pt, edge=float(edge))

    def at_lower_bound(self) -> "FlipSpec":
        """The spec for the lower-bound arm: shifted to its own bound where the file carries one, else as measured."""
        return self.shifted(float(self.edge_lower_bound)) if np.isfinite(float(self.edge_lower_bound)) else self

    def slot_for(self, day: int, index: int, accounts: int = 5) -> int:
        """NQB1's slot rotation: on trading day `day` account `index` takes slot (accounts x day + index) mod the slot
        count, so every slot carries the same share of flips over the cycle and no two accounts share a slot. With one
        slot (D-343: the copied flip at one scheduled minute) every account takes it."""
        return int(self.slots[(int(accounts) * int(day) + int(index)) % len(self.slots)])

    def window_minutes(self, slot: int) -> float:
        """The window a flip at `slot` holds for the cross-account rule: the box when the bracket is boxed (D-343), else
        the slot's own mean minutes to resolution when the spec carries them, else the mean."""
        if self.box_minutes is not None:
            return float(self.box_minutes)
        if self.minutes_by_slot is None:
            return float(self.mean_minutes)
        try:
            return float(self.minutes_by_slot[self.slots.index(int(slot))])
        except ValueError:
            raise ValueError(f"slot {slot} is not one of the flip's decision slots {self.slots}") from None

    def contracts(self, risk: float | None = None) -> int:
        r = self.risk if risk is None else float(risk)
        return max(1, int(round(r / self.risk_per_contract)))

    def as_dict(self) -> dict[str, Any]:
        return {"risk": self.risk, "rr": self.rr, "p_target": self.p_target, "p_stop": self.p_stop, "p_open": self.p_open,
                "p_scratch": self.p_scratch, "scratch_mean_r": self.scratch_mean_r,
                "cost_r": self.cost_r, "risk_per_contract": self.risk_per_contract, "slots": list(self.slots),
                "slot_ct": self.slot_ct, "mean_minutes": self.mean_minutes, "box_minutes": self.box_minutes,
                "minutes_by_slot": None if self.minutes_by_slot is None else list(self.minutes_by_slot),
                "copy": bool(self.copy), "edge": self.edge, "edge_lower_bound": self.edge_lower_bound,
                "net_edge": self.net_edge, "source": self.source}


@dataclass(frozen=True)
class FlipMenu:
    """D-384: a menu of scheduled brackets at one slot -- the collect brackets, the same target under stops of several
    widths -- from which the funded table's decision picks one per session by its risk and R. Every bracket shares the
    slot, the copy and the day's draw (`FlipDraw`'s one uniform a day), so nested brackets agree: under a shared draw a
    target reached under a narrow stop is reached under every wider one, whose target shares are larger."""

    specs: tuple[FlipSpec, ...]

    def __post_init__(self) -> None:
        if not self.specs:
            raise ValueError("a flip menu needs at least one bracket (D-384)")
        s0 = self.specs[0]
        if any(s.slots != s0.slots or bool(s.copy) != bool(s0.copy) for s in self.specs):
            raise ValueError("a flip menu's brackets share one slot set and one copy rule (D-384)")
        keys = [(round(s.risk, 6), round(s.rr, 9)) for s in self.specs]
        if len(set(keys)) != len(keys):
            raise ValueError("each bracket of a flip menu is its own (risk, R) (D-384)")

    @property
    def slots(self) -> tuple[int, ...]:
        return self.specs[0].slots

    @property
    def copy(self) -> bool:
        return bool(self.specs[0].copy)

    @property
    def slot_ct(self) -> str:
        return self.specs[0].slot_ct

    def slot_for(self, day: int, index: int, accounts: int = 5) -> int:
        return self.specs[0].slot_for(day, index, accounts)

    def window_minutes(self, slot: int) -> float:
        """The widest bracket's window -- a default only: the engine reads each account's own bracket's window."""
        return max(s.window_minutes(slot) for s in self.specs)

    def spec_for(self, risk: float, rr: float) -> FlipSpec:
        for s in self.specs:
            if abs(s.rr - float(rr)) < 1e-9 and abs(s.risk - float(risk)) < 1e-6:
                return s
        raise ValueError(f"no bracket of the flip menu at risk {risk:g} and {rr:g}R (D-384)")

    def at_lower_bound(self) -> "FlipMenu":
        return FlipMenu(tuple(s.at_lower_bound() for s in self.specs))

    def as_dict(self) -> dict[str, Any]:
        return {"menu": [s.as_dict() for s in self.specs]}


class FlipDraw:
    """One account's flip outcomes: the bracket's measured shares drawn by calendar day (one uniform per (seed, day):
    accounts sharing a seed share the day's outcome, D-343's copied flip), raced against the room above the floor as
    any trade (`settlement` race: a loss can take no more than the room). The engine calls it like any draw --
    `draw(n, calendar_day, slot, cushion)` -- on the sessions the account's state is a flip state, after setting
    `today` to the day's (slot minute, side) for the ledger. D-384: given a `FlipMenu`, the table's decision picks the
    bracket (`set_risk`) and the day's one uniform settles whichever is picked."""

    settlement = "race"

    def __init__(self, spec: "FlipSpec | FlipMenu", seed: int):
        self.menu = spec if isinstance(spec, FlipMenu) else None
        self.spec = spec.specs[0] if self.menu is not None else spec
        self.seed = int(seed)
        self._risk = float(self.spec.risk)
        self._rr = float(self.spec.rr)
        self.last_trade: dict[str, Any] | None = None
        self.today: tuple[int, int] | None = None     # (slot minute, side) the lockstep sets for the day
        self.flips = 0
        self.won = 0

    def set_risk(self, risk: float, rr: float | None = None) -> None:
        """The table's flip action sizes the flip (whole contracts at the bracket's stop); R as declared. D-384: with a
        menu, the decision's risk and R pick the bracket."""
        if self.menu is not None:
            self.spec = self.menu.spec_for(float(risk), float(rr) if rr is not None else self._rr)
        self._risk = float(risk)
        if rr is not None:
            self._rr = float(rr)

    def uniform(self, day: int) -> float:
        """The day's uniform draw: a function of the seed and the calendar day alone."""
        return float(np.random.default_rng([self.seed, int(day)]).random())

    def __call__(self, n: int, day: int, slot: int, cushion: np.ndarray) -> np.ndarray:
        if int(n) != 1:
            raise ValueError("a flip is one bracket a session")
        s = self.spec
        contracts = s.contracts(self._risk)
        realised = contracts * s.risk_per_contract
        room = float(np.asarray(cushion, float).reshape(-1)[0])
        cost = s.cost_r * realised
        u = self.uniform(day)
        if u < s.p_target:
            pnl, kind = realised * self._rr - cost, "target"
        elif u < s.p_target + s.p_stop:
            pnl, kind = -min(realised, max(room, 0.0)) - cost, "stop"
        elif u < s.p_target + s.p_stop + s.p_open:
            pnl, kind = -min(realised, max(room, 0.0)) - cost, "open"      # open at the flatten: a full loss (NQB1)
        else:
            pnl, kind = max(s.scratch_mean_r * realised, -max(room, 0.0)) - cost, "scratch"   # D-343: closed at the box
        self.flips += 1
        self.won += int(pnl > 0)
        slot_min, side = self.today if self.today is not None else (None, None)
        self.last_trade = {"source": "flip", "contracts": int(contracts), "intended_risk": float(realised),
                           "realised_risk": float(min(realised, max(room, 0.0))), "flip_outcome": kind,
                           "fee": float(cost), "flip_slot": slot_min, "flip_side": side,
                           "flip_window_minutes": (float(s.window_minutes(slot_min)) if slot_min is not None else None)}
        return np.array([pnl], float)


__all__ = ["FlipSpec", "FlipMenu", "FlipDraw", "math"]
