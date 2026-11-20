"""Wave 3.4's synthetic spaces and objectives (no bar, no result file): imported by `tests/test_search_space.py`,
`tests/test_surrogate.py`, `tests/test_proposer.py` and `tests/test_plateau.py`.

* `toy_space()`: three real levers on [0, 1], an integer on 1..7 and a three-cell categorical.
* `smooth(design)`: a known function with its minimum `SMOOTH_MIN` (zero) at `SMOOTH_ARGMIN`.
* `noise(design)`: a rugged surface -- a standard normal fixed by the design's id, so every design's true value differs
  and carries no structure in the levers (the same design reads the same, whatever the seeds).
* `seed_noise(design, seed)`: a standard normal fixed by the design's id and one coin seed: what changes when a design
  is re-read on other seeds.
* `PROTOCOL`: the tests' declared protocol (the composite on two search-year blocks, three seeds, horizon 0);
  `REREAD`: the same with fresh seeds; `sv(...)` and `SV`: what a survey declares to its ledger, the declaration's
  sha256 included; `reading(...)`: a reading on it,
  any field overridden; `evaluator(fn, sd)`: the caller's runner, `fn(design)` plus `sd` times the seed noise under
  each of the protocol's seeds.
* `slot_space()`: two sessions of component slots (windows on a five-minute grid), a dependent latency (a timed source
  `a` with cells 5, 3, 2 and a latency-free `b` with one cell `None`), and a routing lever one of whose cells is a
  tier-1 practice.
* `run_search`: the survey and the declared rounds on an objective, the loop a Wave 5 runner makes of clean runs.

The seeds here are small literals of these tests' own; none is a declared block.
"""
from __future__ import annotations

import hashlib
from typing import Any, Callable, Mapping

import numpy as np

from extended import proposer as P
from extended import search_space as SS

BLOCKS = (("2020-01-02", "2021-12-31"), ("2022-01-03", "2023-12-29"))
OTHER_BLOCKS = (("2020-01-02", "2021-12-31"),)
SEEDS = (101, 102, 103)
REREAD_SEEDS = tuple(range(201, 265))                 # 64 fresh seeds
PROTOCOL = SS.Protocol("composite", BLOCKS, SEEDS, 0)
REREAD = PROTOCOL.with_seeds(REREAD_SEEDS)


def sv(protocol: SS.Protocol = PROTOCOL, reread_seeds=REREAD_SEEDS, measures=()) -> dict[str, Any]:
    """What a survey of these tests declares to its ledger (RB-2): the protocol, the plateau's re-read seeds, the limit
    measures, and the declaration's sha256 of them (rb2-a: the tests' own declaration states its protocol's figure)."""
    return {"protocol": protocol, "reread_seeds": tuple(reread_seeds), "measures": tuple(measures),
            "declaration_sha256": SS.protocol_sha256(protocol, tuple(reread_seeds), tuple(measures))}


#: what every survey of these tests declares by default
SV = sv()
SMOOTH_ARGMIN = {"x1": 0.62, "x2": 0.27, "x3": 0.5, "n": 5, "c": "b"}
SMOOTH_MIN = 0.0
CAT_COST = {"a": 0.3, "b": 0.0, "c": 0.15}


def toy_space() -> SS.Space:
    return SS.Space((SS.Dim("x1", SS.REAL, lo=0.0, hi=1.0), SS.Dim("x2", SS.REAL, lo=0.0, hi=1.0),
                     SS.Dim("x3", SS.REAL, lo=0.0, hi=1.0), SS.Dim("n", SS.INT, lo=1, hi=7, step=1),
                     SS.Dim("c", SS.CAT, values=("a", "b", "c"))))


def smooth(d: Mapping[str, Any]) -> float:
    return (3.0 * (d["x1"] - 0.62) ** 2 + 2.0 * (d["x2"] - 0.27) ** 2 + (d["x3"] - 0.5) ** 2
            + 0.04 * (d["n"] - 5) ** 2 + CAT_COST[d["c"]])


def _h(d: Mapping[str, Any]) -> int:
    return int(hashlib.sha256(SS.design_id(d).encode()).hexdigest()[:15], 16)


def noise(d: Mapping[str, Any]) -> float:
    return float(np.random.default_rng(_h(d)).standard_normal())


def seed_noise(d: Mapping[str, Any], seed: int) -> float:
    return float(np.random.default_rng([_h(d), int(seed)]).standard_normal())


def reading(design: Mapping[str, Any], value: float, *, protocol: SS.Protocol = PROTOCOL, tag: str = "search",
            per_seed=None, se: float | None = None, **over) -> SS.Reading:
    f = dict(blocks=protocol.blocks, seeds=protocol.seeds, measure=protocol.measure, horizon=protocol.horizon)
    f.update(over)
    return SS.Reading(dict(design), float(value), tuple(f["blocks"]), tuple(f["seeds"]), tag, f["measure"],
                      f["horizon"], se, per_seed)


def evaluator(fn: Callable[[Mapping[str, Any]], float], sd: float = 0.0):
    """The caller's runner: per seed, fn(design) + sd * seed_noise(design, seed); the value their mean."""
    def evaluate(design, *, protocol):
        ps = [fn(design) + sd * seed_noise(design, s) for s in protocol.seeds]
        v = float(np.mean(ps))
        se = float(np.std(ps, ddof=1) / np.sqrt(len(ps))) if len(ps) > 1 else 0.0
        return reading(design, v, protocol=protocol, per_seed=ps, se=se)
    return evaluate


def slot_space(routing=("longest_wait", "copy_trade_across_accounts")) -> SS.Space:
    dims = [SS.Dim("routing", SS.CAT, values=tuple(routing)), SS.Dim("risk", SS.REAL, lo=100.0, hi=900.0)]
    slots = []
    for sess, lo, hi, count in (("s1", 0, 100, 2), ("s2", 200, 300, 1)):
        for i in range(count):
            sn = f"{sess}.{i}"
            slots.append(SS.Slot(sn, sess, lo, hi, 5))
            act = (SS.slot_dim(sn, "on"), SS.ON)
            src = SS.slot_dim(sn, "T1")
            dims += [SS.Dim(SS.slot_dim(sn, "on"), SS.CAT, values=(SS.OFF, SS.ON), lever="T2", slot=sn),
                     SS.Dim(src, SS.CAT, values=("a", "b"), active_if=act, lever="T1", slot=sn),
                     SS.Dim(SS.slot_dim(sn, "T4"), SS.CAT, labels=(5, 3, 2, None), active_if=act, lever="T4",
                            slot=sn, cells=lambda d, k=src: (5, 3, 2) if d[k] == "a" else (None,)),
                     SS.Dim(SS.slot_dim(sn, "first"), SS.INT, lo=lo, hi=hi, step=5, active_if=act, lever="T3",
                            slot=sn),
                     SS.Dim(SS.slot_dim(sn, "last"), SS.INT, lo=lo, hi=hi, step=5, after=SS.slot_dim(sn, "first"),
                            active_if=act, lever="T3", slot=sn)]
    return SS.Space(tuple(dims), slots=tuple(slots), fixed={"overlap": "refused"})


def run_search(space: SS.Space, fn, *, survey_n: int, rounds: int, spec: P.RoundSpec, survey_seed: int,
               round_seed: int, ledger: SS.CellLedger, method: str = "sobol", limits=(), limit_fns=None,
               sd: float = 0.0, protocol: SS.Protocol = PROTOCOL):
    ev = evaluator(fn, sd)
    designs = SS.Sampler(space, seed=survey_seed, method=method).survey(
        survey_n, ledger=ledger, **sv(protocol, REREAD_SEEDS, tuple(limit_fns or ())))
    readings = [ev(d, protocol=protocol) for d in designs]
    lim_ev = {m: evaluator(f) for m, f in (limit_fns or {}).items()}
    lim_r = {m: [e(d, protocol=protocol.with_measure(m)) for d in designs] for m, e in lim_ev.items()}
    out = []
    for i in range(1, rounds + 1):
        rnd = P.propose(space, readings, spec=spec, round_index=i, seed=round_seed, ledger=ledger, limits=limits,
                        limit_readings=lim_r or None)
        out.append(rnd)
        readings += [ev(d, protocol=protocol) for d in rnd.designs]
        for m, e in lim_ev.items():
            lim_r[m] += [e(d, protocol=protocol.with_measure(m)) for d in rnd.designs]
    return readings, out
