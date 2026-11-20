"""Wave 3.4 (the restart plan 4.3 e; CHARTER 3.3 (e), 3.9 "the finalist order rule and the plateau rule"): the plateau
check -- a finalist must sit on a plateau, not a spike. Its neighbours, in declared lever steps, are read on a fresh
declared seed set beside **a re-read of the finalist on those same seeds**, and each paired difference must stay within
a declared number of its own standard errors; a finalist that fails is refused, with the reason.

    from extended import plateau as PL
    n = len(ledger.reread.seeds)                 # the re-read seeds the survey declared
    rule = PL.PlateauRule(steps=..., radius=1, tolerance_se=PL.critical_value(0.05, 10, n), margin=0.0,
                          side="worse", min_share=1.0, min_neighbours=4, min_per_lever=1)
    verdict = PL.check(finalist, space, rule, evaluate, ledger=ledger, ledger_seed=S3)
    verdict.accepted, verdict.reason

**The finalist** is a `search_space.Reading` that passes the one door on **the ledger's declared protocol** and is a
counted survey or round cell of the ledger (`search_space.admit`, the red team's B-1 and RB-2). No caller hands the
check a protocol: the selection protocol and the re-read seeds are the ones the survey declared to the ledger. A
surrogate's prediction is never a finalist. The composite is minimised. **The finalist order rule** (which counted cells
are finalists, in what order) is the search declaration's (Wave 5, the red team's m-9); this check takes one finalist.

**The comparison (the red team's B-2, the lead's ruling).** The finalist's own selection reading is the luckiest of
many, so a neighbour compared with it is worse on average even on an exactly flat surface (the winner's curse). So:
- the finalist is **re-read on the fresh seed set the survey declared** (`CellLedger.reread`: the protocol on other
  seeds, disjoint from the selection seeds), and never compared through its selection reading;
- every neighbour is read on the same re-read protocol, so each comparison is paired over the same seeds;
- d = neighbour - re-read, its standard error se from the per-seed paired differences (sd / sqrt(seeds)), and
  z = (d - margin) / se (`side="worse"`: only a worse neighbour counts against the finalist) or (|d| - margin) / se
  (`"two_sided"`). A neighbour **holds** when z <= `tolerance_se`.
The tolerance is in standard-error units of that comparison. **The margin** is the composite's material difference
in its own units (declared; zero allowed): stepping every lever, a categorical's cells included, would otherwise refuse
any finalist whose neighbours differ at all once the re-read has seeds enough to see it. A natural margin is the size
that matters (O-3, the lead's in Wave 4.2).

**The critical value** (the red team's rm-3, the lead's ruling). `critical_value(size, k, n)` is the tolerance at which
a true plateau with k neighbours (each difference at most the margin) is accepted with probability at least 1 - size
under `"worse"` and `min_share=1` -- exactly 1 - size when every difference equals the margin -- for **the statistic as
computed here**: each z a t-statistic on n - 1 degrees of freedom (n the re-read seeds), its se estimated from its own
paired differences, all k sharing the one re-read (so equicorrelated at one half; a seed effect common to the designs
cancels in each pair). Conditional on the re-read's per-seed vector the k statistics are independent; each is (Z +
delta) / sqrt(X / (n - 1)) with delta ~ N(0, 1) from the re-read's mean and X noncentral chi-square on n - 1 degrees of
freedom whose noncentrality is chi-square on n - 1, so P(all hold) = E[G^k] is a quadrature, exact under exchangeable
Gaussian seed noise (`p_all_hold(c, k, n)`). The textbook multivariate t, with one shared denominator, under-covers here
(it does not see k separate se's), and a normal value much more so at small n. `critical_z(size, k)` is the normal limit
(n infinite), kept for reference only. The verdict records the size its tolerance implies at the neighbours actually
read (`size_at`). **The re-read's seed count is part of the rule: it decides the power.** Take a spike twice the
selection readings' sd deep, k = 10 and size 0.05. With as many re-read seeds as the selection used, the power is about
one half; with four times as many it is above nine in ten (`tests/test_plateau.py`'s size-and-power test declares its
own setup). A design-specific effect that does not change with the coin seeds (a fixed history's luck) is not removed by
a re-read: that is the history null's to bound (CHARTER 3.7).

**The neighbourhood** (`neighbours`), every step a declared number of the lever's own units (`PlateauRule.steps`):
- **every lever active in the finalist is stepped** (the red team's m-1), and a rule that leaves one out is refused. A
  categorical takes the step ``"cells"``: each of its other cells. A lever whose cells depend on the stepped lever (a
  source's latency and entry cells), or whose activity it sets (a slot's on/off), is repaired to its centre
  (`Space.repair`), never left invalid;
- ``axes``: each lever moved by -radius .. +radius steps alone (0 excepted); ``box``: `draws` points, each lever moved
  by a whole number of steps drawn uniformly in -radius .. +radius, all at once (the all-zero draw redrawn), from the
  seed's plateau stream (the template's seed `S3`).
The verdict reports three kinds of neighbour that are not read:
- a neighbour outside its lever's bounds is not a design (`outside`);
- a neighbour the space refuses is recorded in the ledger as a refused cell and **reported** (`refused`);
- a lever with no possible step (one cell, a zero-width range) is reported as `unsteppable`.
Every neighbour proposed is a cell of the role ``plateau:<finalist id>``, whose rule sha256 the ledger records (the red
team's m-2), and **a second check of one finalist in one ledger is refused**, under any rule.

**The verdict.** The finalist is **accepted** when all three hold:
- at least `min_neighbours` neighbours were read;
- every steppable lever has at least `min_per_lever` read neighbours;
- the share holding is at least `min_share`.
Otherwise it is **refused**, and the reason names what failed. The verdict records the form (`FORM`), the rule's
sha256, the re-read seeds, and every neighbour's d, se and z.
"""
from __future__ import annotations

import functools
import hashlib
import itertools
import json
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Mapping

import numpy as np
from scipy.optimize import brentq
from scipy.stats import chi2, ncx2, norm

from extended import search_space as SS

TASK = "Wave 3.4"
SIDES = ("worse", "two_sided")
NEIGHBOURHOODS = ("axes", "box")
CELLS = "cells"
FORM = "reread-paired-se"
#: the correlation between two neighbours' differences from one shared re-read, equal variances (exactly one half)
RHO = 0.5
_GH = np.polynomial.hermite_e.hermegauss(96)
#: probability midpoints a level of the exact law's quadrature (checked against a simulation of the statistic)
_QM = 128


class PlateauRefused(ValueError):
    """A rule, a finalist or a neighbour's reading this module cannot stand behind (not a verdict: an error)."""


@functools.lru_cache(maxsize=32)
def _t_grid(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The quadrature of the exact law (the module docstring): Gauss-Hermite nodes for delta, and probability midpoints
    of the noncentrality (chi-square, n - 1) and of X given it (noncentral chi-square, n - 1), as sqrt(X / (n - 1))."""
    nu = int(n) - 1
    d, w = np.polynomial.hermite_e.hermegauss(64)
    q = (np.arange(_QM) + 0.5) / _QM
    lam = chi2.ppf(q, nu)
    x = ncx2.ppf(q[None, :], nu, lam[:, None])
    return d, w / w.sum(), np.sqrt(x / nu)


def p_all_hold(c: float, k: int, n: int | None = None, shift: float = 0.0) -> float:
    """P(every one of k neighbours holds at tolerance c) on a true plateau at the margin: with `n` re-read seeds, the
    exact law of the paired t-statistics (the module docstring); with `n` None, the normal limit (k equicorrelated
    standard normals, shifted by `shift`)."""
    if n is None:
        z, w = _GH
        w = w / w.sum()
        return float(np.sum(w * norm.cdf((c - shift - math.sqrt(RHO) * z) / math.sqrt(1 - RHO)) ** int(k)))
    if shift:
        raise PlateauRefused("the exact law is the plateau's (shift 0); a shifted rate is the normal limit's")
    if int(n) < 2:
        raise PlateauRefused("a paired se needs at least two re-read seeds")
    return _p_exact(float(c), int(k), int(n))


@functools.lru_cache(maxsize=4096)
def _p_exact(c: float, k: int, n: int) -> float:
    d, w, sx = _t_grid(n)
    g = norm.cdf(c * sx[None, :, :] - d[:, None, None]).mean(axis=2)
    return float(np.sum(w * (g ** k).mean(axis=1)))


def critical_value(size: float, k: int, n: int) -> float:
    """The tolerance in standard errors at which a true plateau with k neighbours, compared on n re-read seeds, is
    accepted with probability 1 - size (side 'worse', min_share 1; the module docstring's exact law)."""
    if not 0.0 < size < 1.0 or int(k) < 1:
        raise PlateauRefused("a size in (0, 1) and at least one neighbour")
    return float(brentq(lambda c: p_all_hold(c, k, n) - (1.0 - size), -10.0, 60.0))


def critical_z(size: float, k: int) -> float:
    """The normal limit of `critical_value` (n infinite): for reference, never a rule's tolerance at a finite n."""
    if not 0.0 < size < 1.0 or int(k) < 1:
        raise PlateauRefused("a size in (0, 1) and at least one neighbour")
    return float(brentq(lambda c: p_all_hold(c, k) - (1.0 - size), -10.0, 20.0))


@dataclass(frozen=True)
class PlateauRule:
    """The plateau rule's metric and radius (CHARTER 3.3 (e)); every field declared, none defaulted but the shape."""

    steps: Mapping[str, Any]
    radius: int
    tolerance_se: float
    margin: float
    side: str
    min_share: float
    min_neighbours: int
    min_per_lever: int
    neighbourhood: str = "axes"
    draws: int = 0

    def __post_init__(self) -> None:
        if self.side not in SIDES:
            raise PlateauRefused(f"side is one of {SIDES}")
        if self.neighbourhood not in NEIGHBOURHOODS:
            raise PlateauRefused(f"neighbourhood is one of {NEIGHBOURHOODS}")
        if int(self.radius) < 1 or not self.steps:
            raise PlateauRefused("a radius of at least one step, and at least one stepped lever")
        if not (math.isfinite(self.tolerance_se) and self.tolerance_se >= 0):
            raise PlateauRefused("the tolerance (in standard errors) is finite and non-negative")
        if not (math.isfinite(self.margin) and self.margin >= 0):
            raise PlateauRefused("the margin (in the composite's units) is finite and non-negative")
        if not 0.0 < self.min_share <= 1.0 or int(self.min_neighbours) < 1 or int(self.min_per_lever) < 1:
            raise PlateauRefused("min_share in (0, 1], and at least one neighbour in all and a lever")
        if self.neighbourhood == "box" and int(self.draws) < 1:
            raise PlateauRefused("a box neighbourhood draws at least one point")
        object.__setattr__(self, "steps", dict(self.steps))

    def sha256(self) -> str:
        d = asdict(self)
        d["steps"] = sorted((k, v) for k, v in self.steps.items())
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def validate(self, space: SS.Space, design: Mapping[str, Any] | None = None) -> None:
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
        if design is not None:
            missing = [d.name for d in space.dims if space.active(d, design) and d.name not in self.steps]
            if missing:
                raise PlateauRefused(f"the rule leaves levers active in the finalist unstepped: {missing} (m-1: every "
                                     "active lever is stepped)")


@dataclass
class PlateauVerdict:
    accepted: bool
    reason: str
    finalist: str
    selection_value: float
    reread_value: float
    form: str
    rule: str
    reread_seeds: tuple[int, ...]
    size_at: float
    evaluated: int
    held: int
    share: float
    neighbours: list[dict[str, Any]] = field(default_factory=list)
    refused: list[dict[str, Any]] = field(default_factory=list)
    outside: list[str] = field(default_factory=list)
    per_lever: dict[str, int] = field(default_factory=dict)
    unsteppable: list[str] = field(default_factory=list)
    libs: tuple[tuple[str, str], ...] = SS.LIBS


def _moved(space: SS.Space, design: Mapping[str, Any], name: str, k: int, step: Any) -> dict[str, Any] | None:
    d = space.dim(name)
    out = dict(design)
    x = float(design[name]) + k * float(step)
    lo = float(design[d.after]) if d.after else float(d.lo)
    if not lo - 1e-9 <= x <= float(d.hi) + 1e-9:
        return None
    out[name] = int(round(x)) if d.kind == SS.INT else x
    return out


def _stepped(space: SS.Space, rule: PlateauRule, design: Mapping[str, Any]) -> list[str]:
    """The stepped levers active in `design`, in the space's order (only an active lever is stepped)."""
    return [d.name for d in space.dims if d.name in rule.steps and space.active(d, design)]


def neighbours(space: SS.Space, design: Mapping[str, Any], rule: PlateauRule, *, seed: int | None = None
               ) -> tuple[list[tuple[dict[str, Any], str, tuple[str, ...]]], list[str], list[str]]:
    """([(neighbour, what moved, the levers moved)], [outside], [unsteppable levers]) of `design` under `rule`."""
    rule.validate(space)
    act = _stepped(space, rule, design)
    out: list[tuple[dict[str, Any], str, tuple[str, ...]]] = []
    outside: list[str] = []
    unsteppable: list[str] = []
    if rule.neighbourhood == "axes":
        for name in act:
            d = space.dim(name)
            found = False
            if d.kind == SS.CAT:
                for c in d.cells_of(design):
                    if c != design[name]:
                        nb = dict(design)
                        nb[name] = c
                        out.append((space.repair(nb, [name]), f"{name} -> {c!r}", (name,)))
                        found = True
            else:
                for k in itertools.chain(range(-int(rule.radius), 0), range(1, int(rule.radius) + 1)):
                    nb = _moved(space, design, name, k, rule.steps[name])
                    if nb is None:
                        outside.append(f"{name} {k:+d} step")
                    else:
                        out.append((space.repair(nb, [name]), f"{name} {k:+d} step", (name,)))
                        found = True
            if not found:
                unsteppable.append(name)
        return out, outside, unsteppable
    if seed is None:
        raise PlateauRefused("a box neighbourhood is drawn: give the plateau seed")
    rng = SS.child_rng(seed, SS.STREAM_PLATEAU)
    for name in act:
        d = space.dim(name)
        if d.kind == SS.CAT and len(d.cells_of(design)) < 2:
            unsteppable.append(name)
    for _ in range(int(rule.draws)):
        while True:
            ks = rng.integers(-int(rule.radius), int(rule.radius) + 1, size=len(act))
            if np.any(ks != 0):
                break
        nb: dict[str, Any] | None = dict(design)
        moved, levers = [], []
        for name, k in zip(act, ks):
            if k == 0 or nb is None:
                continue
            d = space.dim(name)
            if d.kind == SS.CAT:
                others = [c for c in d.cells_of(nb) if c != design[name]]
                if others:
                    nb[name] = others[int(rng.integers(len(others)))]
                    moved.append(f"{name} -> {nb[name]!r}")
                    levers.append(name)
                continue
            nb = _moved(space, nb, name, int(k), rule.steps[name])
            if nb is not None:
                moved.append(f"{name} {int(k):+d}")
                levers.append(name)
        if nb is None:
            outside.append("box draw outside the bounds")
        elif moved:
            out.append((space.repair(nb, levers), ", ".join(moved), tuple(levers)))
    return out, outside, unsteppable


def holds(z: float, rule: PlateauRule) -> bool:
    """`z` is (d - margin) / se for 'worse', (|d| - margin) / se for 'two_sided' (`zscore`)."""
    return z <= rule.tolerance_se


def zscore(d: float, se: float, rule: PlateauRule) -> float:
    """The neighbour's distance past the margin, in standard errors of the paired difference."""
    x = (d if rule.side == "worse" else abs(d)) - rule.margin
    return x / se if se > 0 else (0.0 if x == 0 else math.copysign(math.inf, x))


def echoes(got: SS.Reading, design: Mapping[str, Any], protocol: SS.Protocol) -> bool:
    """A reading is of that design, on that protocol's measure, blocks and seeds."""
    return (got.id == SS.design_id(design) and got.measure == protocol.measure and got.blocks == protocol.blocks
            and got.seeds == protocol.seeds)


def _per_seed(r: SS.Reading) -> np.ndarray:
    if r.per_seed is None:
        raise PlateauRefused("the paired comparison needs each reading's per-seed values")
    v = np.asarray(r.per_seed, dtype=float)
    if abs(float(v.mean()) - float(r.value)) > 1e-9 * max(1.0, abs(float(r.value))):
        raise PlateauRefused("a reading's value is the mean of its per-seed values, for the paired comparison")
    return v


def paired(got: SS.Reading, base: SS.Reading) -> tuple[float, float]:
    """(d, se) of `got` against `base`, paired over their common seeds."""
    diff = _per_seed(got) - _per_seed(base)
    d = float(diff.mean())
    se = float(diff.std(ddof=1) / math.sqrt(len(diff))) if len(diff) > 1 else 0.0
    return d, se


def check(finalist: Any, space: SS.Space, rule: PlateauRule, evaluate: Callable[..., Any], *,
          ledger: SS.CellLedger, ledger_seed: int, seed: int | None = None) -> PlateauVerdict:
    """The plateau check (the module docstring). `evaluate(design, protocol=...)` is the caller's runner, handed the
    ledger's re-read protocol; `ledger_seed` the plateau role's seed; `seed` the box stream's. The selection protocol
    and the re-read seeds are the ledger's (declared by the survey), never the caller's."""
    f = SS.admit_one(finalist, ledger=ledger, roles=SS.searched)
    reread = ledger.reread
    why = space.check(f.design)
    if why is not None:
        raise PlateauRefused(f"the finalist is a design the space refuses ({why[0]}: {why[1]})")
    rule.validate(space, f.design)
    role = f"plateau:{f.id}"
    ledger.begin(role, int(ledger_seed), rule=rule.sha256(), reread=list(reread.seeds))
    base = SS.admit_one(evaluate(dict(f.design), protocol=reread), ledger=ledger, reread=True, roles=SS.searched)
    if not echoes(base, f.design, reread):
        raise PlateauRefused("the finalist's re-read was not read as asked: its design on the re-read protocol")
    nbs, outside, unsteppable = neighbours(space, f.design, rule, seed=seed)
    rows: list[dict[str, Any]] = []
    refused: list[dict[str, Any]] = []
    for nb, moved, levers in nbs:
        r = space.check(nb)
        ledger.record(space, nb, role=role, seed=int(ledger_seed), refusal=r)
        if r is not None:
            refused.append({"moved": moved, "levers": list(levers), "class": r[0], "reason": r[1]})
            continue
        got = SS.admit_one(evaluate(nb, protocol=reread), ledger=ledger, reread=True, roles=lambda x: x == role)
        if not echoes(got, nb, reread):
            raise PlateauRefused(f"the neighbour ({moved}) was not read as asked: its design on the re-read protocol")
        d, se = paired(got, base)
        z = zscore(d, se, rule)
        rows.append({"id": got.id, "moved": moved, "levers": list(levers), "value": float(got.value), "delta": d,
                     "se": se, "z": z, "holds": holds(z, rule)})
    per_lever = {name: sum(name in r["levers"] for r in rows) for name in _stepped(space, rule, f.design)
                 if name not in unsteppable}
    n = len(rows)
    held = sum(r["holds"] for r in rows)
    share = held / n if n else 0.0
    size_at = (1.0 - p_all_hold(rule.tolerance_se, n, len(reread.seeds))) if n and rule.side == "worse" \
        else float("nan")
    out = dict(finalist=f.id, selection_value=float(f.value), reread_value=float(base.value), form=FORM,
               rule=rule.sha256(), reread_seeds=tuple(reread.seeds), size_at=size_at, evaluated=n, held=held,
               share=share,
               neighbours=rows, refused=refused, outside=outside, per_lever=per_lever, unsteppable=unsteppable)
    thin = {k: v for k, v in per_lever.items() if v < int(rule.min_per_lever)}
    if n < int(rule.min_neighbours) or thin:
        reason = (f"refused: {n} neighbour(s) read (the rule's minimum {rule.min_neighbours}); levers with fewer than "
                  f"{rule.min_per_lever} read: {sorted(thin)}; {len(outside)} outside the bounds, {len(refused)} "
                  "refused by the space")
        return PlateauVerdict(False, reason, **out)
    worst = max(rows, key=lambda r: r["z"])
    if share + 1e-12 < rule.min_share:
        reason = (f"refused: a spike, not a plateau -- {held} of {n} neighbours hold within {rule.tolerance_se} "
                  f"standard errors of the finalist's re-read ({rule.side}; share {share:.3f} below "
                  f"{rule.min_share}); the worst, {worst['moved']}, at z {worst['z']:+.3g}")
        return PlateauVerdict(False, reason, **out)
    reason = (f"accepted: {held} of {n} neighbours hold within {rule.tolerance_se} standard errors of the finalist's "
              f"re-read ({rule.side}); the worst, {worst['moved']}, at z {worst['z']:+.3g}")
    return PlateauVerdict(True, reason, **out)


__all__ = ["TASK", "SIDES", "NEIGHBOURHOODS", "CELLS", "FORM", "RHO", "PlateauRefused", "p_all_hold",
           "critical_value", "critical_z",
           "PlateauRule", "PlateauVerdict", "neighbours", "holds", "zscore", "echoes", "paired", "check"]
