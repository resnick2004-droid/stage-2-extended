"""Wave 3.4 (the restart plan 4.3 d; CHARTER 3.3 (d), (f), (g); the template's section 6 "the rounds"): the round
proposer -- the next batch of designs to read, from the surrogate, at a fixed budget a round, every proposed cell
counted and the round's seed recorded. It proposes; it never reads, and it never names a finalist.

    from extended import proposer as P
    spec = P.RoundSpec(batch=8, pool=1024, acquisition="ei")
    rnd = P.propose(space, readings, spec=spec, round_index=1, seed=S2, ledger=ledger)
    rnd.designs                                    # exactly `spec.batch` designs, each recorded as `round-1`

**One round** (`propose`):
0. **Begin** the round in the cell ledger (`CellLedger.begin`): a round number already recorded, under any seed, is
   refused, and so is a round before the one before it (the red team's B-1) -- a round is drawn once, never re-drawn
   under a new seed for the reader to choose from.
1. **Fit** the composite's surrogate (`extended.surrogate.Surrogate.fit`, the one door: every reading tagged
   ``search`` and inside the search years) with the seed's fit stream keyed by the round; and one surrogate a declared
   limit
   (`Limit`: a measure, its bound and direction), each on its own measure's readings, through the same door.
2. **Candidates**: a scrambled Sobol pool of `spec.pool` unit points from the round seed's pool stream, and
   `spec.local` Gaussian perturbations (scale `spec.local_scale` on the unit cube) around each of the
   `spec.centres` read designs with the lowest predicted composite, from its local stream; each decoded and checked by
   the space (`Space.check`); refused candidates, designs already read and repeats dropped. A candidate is not a cell:
   only a proposal is. The pool's counts are in the round's record.
3. **Acquisition** for a minimised composite: expected improvement below the incumbent (the lowest predicted mean
   over the read designs, so one lucky reading does not set it), `ei`, less `spec.xi`; or the lower confidence bound
   mu - kappa sd, `lcb`. Under limits, `ei` is multiplied by the probability that every limit holds (each limit's
   surrogate, independent normals); `lcb` keeps the candidates whose probability is at least `spec.p_feasible`
   (all, if none reaches it, ordered by that probability first).
4. **The batch** by the kriging believer: the best candidate is taken, the composite's surrogate is conditioned on
   its own predicted mean there (`Surrogate.believe`), the acquisition recomputed, and so on until `spec.batch`
   designs are taken. A pool holding fewer valid candidates than the batch refuses the round (the budget is declared,
   never shrunk after a look).
5. **Counted**: every proposal enters the cell ledger as ``round-<i>`` with the round seed.
The number of rounds is the declaration's, never extended after a look; nothing here decides to stop or continue.

**One protocol** (the red team's m-10 and RB-2): every reading -- the composite's and each limit's -- passes the one
door on the ledger's declared protocol (`search_space.admit`), a limit's on the same blocks, seeds and horizon under
its own measure, which the survey must have declared; no caller hands a round a protocol.
**Single objective under limits** is this engine's reading of CHARTER 3.3 (d)'s "constrained, multi-objective"
optimisation: the composite is the objective and the limits are constraints by probability of feasibility. The
multi-objective frontier and the finalist order rule are the search declaration's (Wave 5, the lead's ruling); `limits`
and one surrogate a measure are their hooks, and every reading the frontier would need is a counted cell on the
protocol.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.stats import norm, qmc

from extended import search_space as SS
from extended import surrogate as SG

TASK = "Wave 3.4"
ACQUISITIONS = ("ei", "lcb")
DIRECTIONS = ("<=", ">=")


class ProposerRefused(ValueError):
    """A round this module cannot stand behind."""


@dataclass(frozen=True)
class RoundSpec:
    """A round's declared parameters (the template's section 6)."""

    batch: int
    pool: int
    acquisition: str
    kappa: float = 2.0
    xi: float = 0.0
    centres: int = 4
    local: int = 64
    local_scale: float = 0.05
    restarts: int = 4
    p_feasible: float = 0.5

    def __post_init__(self) -> None:
        if self.acquisition not in ACQUISITIONS:
            raise ProposerRefused(f"unknown acquisition {self.acquisition!r}; one of {ACQUISITIONS}")
        if int(self.batch) < 1 or int(self.pool) < 1 or (int(self.pool) & (int(self.pool) - 1)):
            raise ProposerRefused("a batch is at least one design and a Sobol pool a power of two")
        if min(self.centres, self.local, self.restarts) < 0 or self.local_scale <= 0 or self.kappa < 0:
            raise ProposerRefused("counts are non-negative, the local scale positive, kappa non-negative")
        if not 0.0 < self.p_feasible <= 1.0:
            raise ProposerRefused("p_feasible lies in (0, 1]")


@dataclass(frozen=True)
class Limit:
    """A declared limit on a measure: its readings must satisfy value `direction` bound."""

    measure: str
    bound: float
    direction: str

    def __post_init__(self) -> None:
        if self.direction not in DIRECTIONS:
            raise ProposerRefused(f"a limit's direction is one of {DIRECTIONS}")


@dataclass
class Round:
    index: int
    seed: int
    spec: RoundSpec
    designs: list[dict[str, Any]]
    acquisition: list[float]
    mean: list[float]
    sd: list[float]
    p_feasible: list[float]
    incumbent: float
    candidates: dict[str, int]
    fit: SG.FitRecord
    limit_fits: dict[str, SG.FitRecord] = field(default_factory=dict)
    libs: tuple[tuple[str, str], ...] = SS.LIBS


def expected_improvement(mu: np.ndarray, sd: np.ndarray, best: float, xi: float) -> np.ndarray:
    """Expected improvement below `best` (minimising)."""
    imp = best - mu - xi
    z = imp / sd
    return imp * norm.cdf(z) + sd * norm.pdf(z)


def lower_confidence(mu: np.ndarray, sd: np.ndarray, kappa: float) -> np.ndarray:
    """The negated lower confidence bound (larger is better), minimising."""
    return -(mu - kappa * sd)


def p_limits(fits: Sequence[tuple[Limit, SG.Surrogate]], designs: Sequence[Mapping[str, Any]]) -> np.ndarray:
    """The probability that every limit holds at each design (independent normals)."""
    p = np.ones(len(designs))
    for lim, sg in fits:
        pr = sg.predict(designs)
        z = (lim.bound - pr.mean) / pr.sd
        p *= norm.cdf(z) if lim.direction == "<=" else norm.cdf(-z)
    return p


def _candidates(space: SS.Space, sg: SG.Surrogate, read: Sequence[Mapping[str, Any]], spec: RoundSpec,
                seed: int, round_index: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    seen = {SS.design_id(d) for d in read}
    out: list[dict[str, Any]] = []
    stats = {"pool": 0, "pool_refused": 0, "local": 0, "local_refused": 0, "repeats": 0}

    def take(design: dict[str, Any], kind: str) -> None:
        stats[kind] += 1
        if space.check(design) is not None:
            stats[f"{kind}_refused"] += 1
            return
        i = SS.design_id(design)
        if i in seen:
            stats["repeats"] += 1
            return
        seen.add(i)
        out.append(design)

    eng = qmc.Sobol(space.d, scramble=True, seed=SS.child_rng(seed, SS.STREAM_POOL, round_index))
    for u in eng.random_base2(int(round(math.log2(spec.pool)))):
        take(space.decode(u), "pool")
    if spec.centres and spec.local and read:
        mu = sg.predict(read).mean
        order = np.argsort(mu, kind="stable")[:spec.centres]
        rng = SS.child_rng(seed, SS.STREAM_LOCAL, round_index)
        for i in order:
            u0 = space.unit_of(read[int(i)])
            for _ in range(spec.local):
                u = np.clip(u0 + rng.normal(0.0, spec.local_scale, size=space.d), 0.0, np.nextafter(1.0, 0.0))
                take(space.decode(u), "local")
    stats["valid"] = len(out)
    return out, stats


def propose(space: SS.Space, readings: Sequence[Any], *, spec: RoundSpec, round_index: int, seed: int,
            ledger: SS.CellLedger, limits: Sequence[Limit] = (),
            limit_readings: Mapping[str, Sequence[Any]] | None = None) -> Round:
    """One round (the module docstring)."""
    SS.child_rng(seed)
    if type(round_index) is not int or round_index < 1:
        raise ProposerRefused("rounds are numbered from one (the survey is round zero's role)")
    for lim in limits:
        if not (limit_readings or {}).get(lim.measure):
            raise ProposerRefused(f"a limit on {lim.measure!r} needs that measure's readings")
    for lim in limits:
        ledger.protocol_for(lim.measure)                      # a limit the survey did not declare is refused
    ledger.begin(f"round-{round_index}", int(seed))
    sg = SG.Surrogate(space, seed=seed, restarts=spec.restarts, measure=ledger.protocol.measure,
                      key=(int(round_index), 0))
    fit = sg.fit(readings, ledger=ledger)
    fits: list[tuple[Limit, SG.Surrogate]] = []
    limit_fits: dict[str, SG.FitRecord] = {}
    for li, lim in enumerate(limits):
        rs = (limit_readings or {})[lim.measure]
        ls = SG.Surrogate(space, seed=seed, restarts=spec.restarts, measure=lim.measure,
                          key=(int(round_index), li + 1))
        limit_fits[lim.measure] = ls.fit(rs, ledger=ledger)
        fits.append((lim, ls))
    read = [r.design for r in SS.admit(readings, ledger=ledger)]
    cands, stats = _candidates(space, sg, read, spec, seed, int(round_index))
    if len(cands) < spec.batch:
        raise ProposerRefused(f"{len(cands)} valid candidates for a batch of {spec.batch}: the round is refused, "
                              "never shrunk")
    pf = p_limits(fits, cands) if fits else np.ones(len(cands))
    incumbent = float(np.min(sg.predict(read).mean))
    left = list(range(len(cands)))
    chosen, acq_v, mu_v, sd_v, pf_v = [], [], [], [], []
    cur = sg
    for _ in range(spec.batch):
        sub = [cands[i] for i in left]
        pr = cur.predict(sub)
        p = pf[left]
        if spec.acquisition == "ei":
            a = expected_improvement(pr.mean, pr.sd, incumbent, spec.xi) * p
            key = a
        else:
            a = lower_confidence(pr.mean, pr.sd, spec.kappa)
            ok = p >= spec.p_feasible
            key = np.where(ok, a, -np.inf) if ok.any() else p
        j = int(np.argmax(key))
        i = left.pop(j)
        chosen.append(cands[i])
        acq_v.append(float(a[j]))
        mu_v.append(float(pr.mean[j]))
        sd_v.append(float(pr.sd[j]))
        pf_v.append(float(p[j]))
        cur = cur.believe([cands[i]])
    for d in chosen:
        ledger.record(space, d, role=f"round-{int(round_index)}", seed=int(seed), refusal=None,
                      round_index=int(round_index))
    return Round(int(round_index), int(seed), spec, chosen, acq_v, mu_v, sd_v, pf_v, incumbent, stats, fit,
                 limit_fits, SS.LIBS)


__all__ = ["TASK", "ACQUISITIONS", "DIRECTIONS", "ProposerRefused", "RoundSpec", "Limit", "Round",
           "expected_improvement", "lower_confidence", "p_limits", "propose"]
