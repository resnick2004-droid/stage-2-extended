"""Stand-ins for the vendored risk policy and draw, in process, for `tests/test_survey_route.py`'s unit tests of
`survey_route.check_policy_reads` and `survey_route.AccountingDraw` (the vendored tree is never put on this process's
path). Their shapes are the vendored ones the route reads (`propedge.campaign.risk_policy`: a policy's `root.leaves`,
a leaf's `name`, `risk`, `rr`, `max_trades`, `abandon`, `source`; `propedge.campaign.sizing.TierSizedDraw`: `_rr`,
`stats`, `last_trade`, a call returning one outcome). The real ones go through the route in the child process
(`tests/survey_route_child.py race`)."""
from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import numpy as np

PHASES = ("combine", "funded", "paid")


@dataclass(frozen=True)
class Leaf:
    name: str
    risk: float
    rr: float | None = None
    max_trades: int | None = None
    abandon: bool = False
    source: str = "strategy"

    def leaves(self, phases):
        yield self, phases


@dataclass(frozen=True)
class Phase:
    combine: Any
    funded: Any

    def leaves(self, phases):
        yield from self.combine.leaves(frozenset({"combine"}))
        yield from self.funded.leaves(frozenset({"funded", "paid"}))


@dataclass(frozen=True)
class Policy:
    id: str
    root: Any


def policy(combine: Leaf, funded: Leaf) -> Policy:
    return Policy("stand-in", Phase(combine, funded))


@dataclass
class TierSizedDraw:
    """A draw stand-in: each call plays the next of `script` -- 'none' (no trade at the slot), 'taken', 'stood_aside',
    'unsized', 'no_outcome' or 'nan' (a trade dropped with a NaN outcome)."""

    script: list
    _rr: float | None = 1.5
    stats: Any = field(default_factory=lambda: SimpleNamespace(trades=0, stood_aside=0, unsized=0, no_outcome=0))
    last_trade: Any = None

    def __call__(self, n, day, slot, cushion, **kw):
        what = self.script.pop(0)
        self.last_trade = None
        if what == "none":
            return np.array([np.nan])
        if what == "no_outcome":
            self.stats.no_outcome += 1
            return np.array([np.nan])
        if what == "stood_aside":
            self.stats.stood_aside += 1
            self.last_trade = {"stood_aside": True}
            return np.array([np.nan])
        self.stats.trades += 1
        self.last_trade = {"historical_day": 0, "trade_index": 0, "u": np.nan if what == "nan" else 0.5}
        if what == "unsized":
            self.stats.unsized += 1
            return np.array([np.nan])
        return np.array([np.nan if what == "nan" else 50.0])


class SharedDayDraw(TierSizedDraw):
    """The vendored unsized draw's name: a reader of the pnl channel."""
