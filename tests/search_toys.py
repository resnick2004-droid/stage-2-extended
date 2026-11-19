"""Wave 3.4's synthetic spaces and objectives (no bar, no result file): imported by `tests/test_search_space.py`,
`tests/test_surrogate.py`, `tests/test_proposer.py` and `tests/test_plateau.py`.

* `toy_space()`: three real levers on [0, 1], an integer on 1..7 and a three-cell categorical.
* `smooth(design)`: a known function with its minimum `SMOOTH_MIN` (zero) at `SMOOTH_ARGMIN`.
* `noise(design)`: a pure-noise objective -- a standard normal fixed by the design's id (the same design, the same
  blocks and seeds, the same reading), carrying no structure in the levers.
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


def noise(d: Mapping[str, Any]) -> float:
    h = int(hashlib.sha256(SS.design_id(d).encode()).hexdigest()[:16], 16)
    return float(np.random.default_rng(h).standard_normal())


def reading(design: Mapping[str, Any], value: float, *, tag: str = "search", blocks=BLOCKS, seeds=SEEDS,
            measure: str = "composite", se: float | None = None) -> SS.Reading:
    return SS.Reading(dict(design), float(value), tuple(blocks), tuple(seeds), tag, measure, se)


def evaluator(fn: Callable[[Mapping[str, Any]], float], measure: str = "composite"):
    def evaluate(design, *, blocks, seeds):
        return reading(design, fn(design), blocks=blocks, seeds=seeds, measure=measure)
    return evaluate


def slot_space(routing=("longest_wait", "copy_trade_across_accounts")) -> SS.Space:
    dims =[SS.Dim("routing", SS.CAT, values=tuple(routing)), SS.Dim("risk", SS.REAL, lo=100.0, hi=900.0)]
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
               round_seed: int, ledger: SS.CellLedger, method: str = "sobol", limits=(), limit_fns=None):
    designs = SS.Sampler(space, seed=survey_seed, method=method).survey(survey_n, ledger=ledger)
    readings = [reading(d, fn(d)) for d in designs]
    lim_r = {m: [reading(d, f(d), measure=m) for d in designs] for m, f in (limit_fns or {}).items()}
    out = []
    for i in range(1, rounds + 1):
        rnd = P.propose(space, readings, spec=spec, round_index=i, seed=round_seed, ledger=ledger, limits=limits,
                        limit_readings=lim_r or None)
        out.append(rnd)
        readings += [reading(d, fn(d)) for d in rnd.designs]
        for m, f in (limit_fns or {}).items():
            lim_r[m] += [reading(d, f(d), measure=m) for d in rnd.designs]
    return readings, out
