"""Wave 3.4 (the restart plan 4.3 e; CHARTER 3.3 (e), 3.9 "the finalist order rule and the plateau rule"): the plateau
check -- a finalist must sit on a plateau, not a spike. Its neighbours, in declared lever steps, are read on the
finalist's own search-year blocks and coin seeds, and must hold the composite within a declared tolerance; a finalist
that fails is refused, with the reason.

    from extended import plateau as PL
    rule = PL.PlateauRule(steps={"S2": 0.1, "A7": 1, "ny.0.first": 5}, radius=1, tolerance=tol, side="worse",
                          min_share=1.0, min_neighbours=4)
    verdict = PL.check(finalist_reading, space, rule, evaluate, ledger=ledger)
    verdict.accepted, verdict.reason

**The finalist** is a `search_space.Reading` that passes the one door (`search_space.admit`: tagged ``search``, every
block inside the search years); a surrogate's prediction is never a finalist. Its composite is minimised (lower is
better), as `extended.proposer`'s is.

**The neighbourhood** (`neighbours`), every step a declared number of the lever's own units (`PlateauRule.steps`):
* ``axes``: from the finalist, each stepped lever moved by -radius .. +radius steps alone (0 excepted); a categorical
  given the step ``"cells"`` takes each of its other cells (radius aside);
* ``box``: `draws` points, each stepped lever moved by a whole number of steps drawn uniformly in -radius .. +radius,
  all at once (the all-zero draw redrawn), from the seed's plateau stream (the template's seed `S3`).
A neighbour outside its lever's bounds is not a design and is skipped (counted as ``outside``); a neighbour the space
refuses (`Space.check`: a window collision, a rule, conduct tier 1) is recorded in the cell ledger as refused and
skipped; a lever inactive in the finalist (an off slot) is not stepped. Every neighbour read is recorded in the cell
ledger as ``plateau``.

**The reading** (`evaluate(design, blocks=..., seeds=...)`, the caller's runner): each neighbour on the finalist's own
blocks and seeds. Its reading must pass the one door and echo that design, measure, blocks and seeds, or the check
stops (`PlateauRefused`): a neighbour read on other blocks is not a neighbour's reading.

**The rule** (pinned with 3.9's inputs): with d = neighbour - finalist, a neighbour **holds** when d <= tolerance
(`side="worse"`: only a worse neighbour counts against the finalist) or |d| <= tolerance (`"two_sided"`: the
composite held within the tolerance either way). The finalist is **accepted** when at least `min_neighbours`
neighbours were read and the share holding is at least `min_share`; otherwise **refused**, the reason naming the
counts, the share and the worst neighbour's move.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

import numpy as np

from extended import search_space as SS

TASK = "Wave 3.4"
SIDES = ("worse", "two_sided")
NEIGHBOURHOODS = ("axes", "box")
CELLS = "cells"


class PlateauRefused(ValueError):
    """A rule, a finalist or a neighbour's reading this module cannot stand behind (not a verdict: an error)."""


@dataclass(frozen=True)
class PlateauRule:
    """The plateau rule's metric and radius (CHARTER 3.3 (e)); every field declared, none defaulted but the shape."""

    steps: Mapping[str, Any]
    radius: int
    tolerance: float
    side: str
    min_share: float
    min_neighbours: int
    neighbourhood: str = "axes"
    draws: int = 0

    def __post_init__(self) -> None:
        if self.side not in SIDES:
            raise PlateauRefused(f"side is one of {SIDES}")
        if self.neighbourhood not in NEIGHBOURHOODS:
            raise PlateauRefused(f"neighbourhood is one of {NEIGHBOURHOODS}")
        if int(self.radius) < 1 or not self.steps:
            raise PlateauRefused("a radius of at least one step, and at least one stepped lever")
        if not (math.isfinite(self.tolerance) and self.tolerance >= 0):
            raise PlateauRefused("the tolerance is finite and non-negative")
        if not 0.0 < self.min_share <= 1.0 or int(self.min_neighbours) < 1:
            raise PlateauRefused("min_share in (0, 1] and at least one neighbour")
        if self.neighbourhood == "box" and int(self.draws) < 1:
            raise PlateauRefused("a box neighbourhood draws at least one point")

    def validate(self, space: SS.Space) -> None:
        for name, step in self.steps.items():
            d = space.dim(name)
            if d.kind == SS.CAT:
                if step != CELLS:
                    raise PlateauRefused(f"{name}: a categorical's step is {CELLS!r}")
                continue
            if isinstance(step, bool) or not isinstance(step, (int, float)) or not step > 0:
                raise PlateauRefused(f"{name}: a positive step in the lever's units")
            if d.step is not None:
                k = float(step) / float(d.step)
                if abs(k - round(k)) > 1e-9:
                    raise PlateauRefused(f"{name}: the step {step} is not a whole number of its lattice step {d.step}")


@dataclass
class PlateauVerdict:
    accepted: bool
    reason: str
    finalist: str
    value: float
    evaluated: int
    held: int
    share: float
    neighbours: list[dict[str, Any]] = field(default_factory=list)
    skipped: dict[str, int] = field(default_factory=dict)


def _moved(space: SS.Space, design: Mapping[str, Any], name: str, k: int, step: Any) -> dict[str, Any] | None:
    d = space.dim(name)
    v = design[name]
    out = dict(design)
    x = float(v) + k * float(step)
    lo = float(design[d.after]) if d.after else float(d.lo)
    if not lo - 1e-9 <= x <= float(d.hi) + 1e-9:
        return None
    out[name] = int(round(x)) if d.kind == SS.INT else x
    return out


def neighbours(space: SS.Space, design: Mapping[str, Any], rule: PlateauRule, *, seed: int | None = None
               ) -> tuple[list[tuple[dict[str, Any], str]], int]:
    """([(neighbour design, what moved)], how many fell outside the bounds) of `design` under `rule`."""
    rule.validate(space)
    act = [n for n in rule.steps if space.active(space.dim(n), design)]
    out: list[tuple[dict[str, Any], str]] = []
    outside = 0
    if rule.neighbourhood == "axes":
        for name in act:
            d = space.dim(name)
            if d.kind == SS.CAT:
                for c in d.cells_of(design):
                    if c != design[name]:
                        nb = dict(design)
                        nb[name] = c
                        out.append((nb, f"{name} -> {c!r}"))
                continue
            for k in itertools.chain(range(-int(rule.radius), 0), range(1, int(rule.radius) + 1)):
                nb = _moved(space, design, name, k, rule.steps[name])
                if nb is None:
                    outside += 1
                else:
                    out.append((nb, f"{name} {k:+d} step"))
        return out, outside
    if seed is None:
        raise PlateauRefused("a box neighbourhood is drawn: give the plateau seed")
    rng = SS.child_rng(seed, SS.STREAM_PLATEAU)
    for _ in range(int(rule.draws)):
        while True:
            ks = rng.integers(-int(rule.radius), int(rule.radius) + 1, size=len(act))
            if np.any(ks != 0):
                break
        nb: dict[str, Any] | None = dict(design)
        moved = []
        for name, k in zip(act, ks):
            if k == 0:
                continue
            d = space.dim(name)
            if d.kind == SS.CAT:
                others = [c for c in d.cells_of(nb) if c != design[name]]
                if others:
                    nb[name] = others[int(rng.integers(len(others)))]
                    moved.append(f"{name} -> {nb[name]!r}")
                continue
            nb = _moved(space, nb, name, int(k), rule.steps[name])
            if nb is None:
                break
            moved.append(f"{name} {int(k):+d}")
        if nb is None:
            outside += 1
        elif moved:
            out.append((nb, ", ".join(moved)))
    return out, outside


def holds(delta: float, rule: PlateauRule) -> bool:
    return delta <= rule.tolerance if rule.side == "worse" else abs(delta) <= rule.tolerance


def echoes(got: SS.Reading, design: Mapping[str, Any], finalist: SS.Reading) -> bool:
    """A neighbour's reading is of that design, on the finalist's measure, blocks and seeds."""
    return (got.id == SS.design_id(design) and got.measure == finalist.measure and got.blocks == finalist.blocks
            and got.seeds == finalist.seeds)


def check(finalist: Any, space: SS.Space, rule: PlateauRule,
          evaluate: Callable[..., Any], *, ledger: SS.CellLedger, ledger_seed: int,
          seed: int | None = None) -> PlateauVerdict:
    """The plateau check (the module docstring). `ledger_seed` is the seed the neighbours' cells are recorded with
    (the coin seed set's role seed); `seed` the plateau stream's, for a box."""
    f = SS.admit_one(finalist)
    why = space.check(f.design)
    if why is not None:
        raise PlateauRefused(f"the finalist is a design the space refuses ({why[0]}: {why[1]})")
    nbs, outside = neighbours(space, f.design, rule, seed=seed)
    rows: list[dict[str, Any]] = []
    refused = 0
    for nb, moved in nbs:
        r = space.check(nb)
        ledger.record(space, nb, role="plateau", seed=int(ledger_seed), refusal=r)
        if r is not None:
            refused += 1
            continue
        got = SS.admit_one(evaluate(nb, blocks=f.blocks, seeds=f.seeds))
        if not echoes(got, nb, f):
            raise PlateauRefused(f"the neighbour ({moved}) was not read as asked: its design, measure, blocks and "
                                 "seeds are the finalist's protocol")
        delta = float(got.value) - float(f.value)
        rows.append({"id": got.id, "moved": moved, "value": float(got.value), "delta": delta,
                     "holds": holds(delta, rule)})
    n = len(rows)
    held = sum(r["holds"] for r in rows)
    share = held / n if n else 0.0
    skipped = {"outside": outside, "refused": refused}
    if n < int(rule.min_neighbours):
        reason = (f"refused: {n} neighbour(s) read, fewer than the rule's {rule.min_neighbours} "
                  f"({outside} outside the bounds, {refused} refused by the space)")
        return PlateauVerdict(False, reason, f.id, float(f.value), n, held, share, rows, skipped)
    worst = max(rows, key=lambda r: r["delta"] if rule.side == "worse" else abs(r["delta"]))
    if share + 1e-12 < rule.min_share:
        reason = (f"refused: a spike, not a plateau -- {held} of {n} neighbours hold the composite within "
                  f"{rule.tolerance} ({rule.side}; share {share:.3f} below {rule.min_share}); the worst, "
                  f"{worst['moved']}, moves it by {worst['delta']:+.6g}")
        return PlateauVerdict(False, reason, f.id, float(f.value), n, held, share, rows, skipped)
    reason = (f"accepted: {held} of {n} neighbours hold the composite within {rule.tolerance} ({rule.side}); the "
              f"worst, {worst['moved']}, moves it by {worst['delta']:+.6g}")
    return PlateauVerdict(True, reason, f.id, float(f.value), n, held, share, rows, skipped)


__all__ = ["TASK", "SIDES", "NEIGHBOURHOODS", "CELLS", "PlateauRefused", "PlateauRule", "PlateauVerdict",
           "neighbours", "holds", "echoes", "check"]
