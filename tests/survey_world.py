"""The Wave 5 survey runner's synthetic world (no bar, no result file of the repository): imported by
`tests/test_survey.py`.

* `engine()`: Wave 3.4's engine as it stood (`search_space`, `surrogate`, `proposer`, `plateau` at df367a7, merged into
  this branch), checked by `survey.Engine.check`.
* `space(SS)`: `x` 0..1 step 0.1, `y` 0..20 step 2 (integer), `k` a/b.
* `World(kind)`: the toy three-way runner. For a design and the four baselines it reports a start-by-seed matrix of
  `money` = f(design) + a common seed effect (the coins every arm shares) + idiosyncratic coin noise, `risk` (a limit
  measure) and `supply` (the gate's), the design's real-path as-traded and reflected `money`, where its sides come
  from, and its positions. Every design it runs is logged (`calls`). Its settings are its `survey_config()`, so a world
  of another kind is another part (S-3). The kinds:
  - ``plateau``: a broad bump of height `A` at x 0.7, y 12; ``spike``: `A` only at x = 0.3; ``noise``: f = 0;
  - ``near``: the bump at height `A_NEAR`, its composite gain between the margin and the margin plus z standard errors;
  - ``strong``: the bump, with P-16 stronger than every design and the other three baselines at zero;
  - ``limit``: the bump, its `risk` above the bound wherever the bump is;
  - ``harm``: the bump, its as-traded real path worse than the reflected by more than the no-harm margin there;
  - ``coin_side``: the bump, its sides there from the coin, not the trigger;
  - ``hedge``: the bump on k = b only, where every design opens two opposite positions on two accounts at once;
  - ``gated``: the bump, its supply below the gate's floor there;
  - ``unpaired``: the bump, the baselines run on one start fewer than the design.
  `tag`, `blocks` and `horizon` override the run's report (the held-out refusals).
* `spec(bound)`: the tests' declared numbers with the parts' bindings; `declaration(spec)`: a declaration's text.

The seeds here are small literals of these tests' own; none is a declared block.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Mapping

import numpy as np

A = 2.0            # the planted height, in money's units (the composite's span is 6)
A_NEAR = 0.76      # a composite gain near 0.12: past the margin 0.1, short of the margin plus z = 3 standard errors
SIGMA = 0.5        # the idiosyncratic coin noise per unit
STARTS = 3
KINDS = ("plateau", "spike", "noise", "near", "strong", "limit", "harm", "coin_side", "hedge", "gated", "unpaired")

_ENGINE: Any = None


def engine():
    global _ENGINE
    if _ENGINE is None:
        from extended import plateau, proposer, search_space, surrogate
        _ENGINE = (search_space, surrogate, proposer, plateau)
    return _ENGINE


def space(SS, *, x_hi: float = 1.0, extra=()):
    return SS.Space((SS.Dim("x", SS.REAL, lo=0.0, hi=x_hi, step=0.1), SS.Dim("y", SS.INT, lo=0, hi=20, step=2),
                     SS.Dim("k", SS.CAT, values=("a", "b"))) + tuple(extra), fixed={"overlap": "refused"})


def bump(d: Mapping[str, Any], height: float = A) -> float:
    return height * float(np.exp(-((d["x"] - 0.7) / 0.3) ** 2 - ((d["y"] - 12) / 8.0) ** 2))


def f_true(kind: str, d: Mapping[str, Any]) -> float:
    if kind == "spike":
        return A if abs(d["x"] - 0.3) < 1e-9 else 0.0
    if kind == "noise":
        return 0.0
    if kind == "near":
        return bump(d, A_NEAR)
    if kind == "hedge":
        return bump(d) if d["k"] == "b" else 0.0
    return bump(d)


def _h(*parts: Any) -> int:
    return int(hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:15], 16)


class World:
    def __init__(self, kind: str, *, tag: str = "search", blocks=None, horizon: int | None = None):
        if kind not in KINDS:
            raise ValueError(kind)
        self.kind, self.tag, self.blocks, self.horizon = kind, tag, blocks, horizon
        self.calls: list[str] = []

    def survey_config(self) -> dict[str, Any]:
        return {"kind": self.kind, "tag": self.tag, "blocks": self.blocks, "horizon": self.horizon, "A": A,
                "A_NEAR": A_NEAR, "SIGMA": SIGMA, "STARTS": STARTS}

    def build_schedule(self, design: Mapping[str, Any]) -> Any:
        return ("toy-schedule", json.dumps(dict(design), sort_keys=True))

    def runner(self, schedule: Any, protocol: Any):
        from extended import components as C
        from extended import survey as SV

        SS = engine()[0]
        design = json.loads(schedule[1])
        did = SS.design_id(design)
        self.calls.append(did)
        seeds = protocol.seeds
        common = np.array([np.random.default_rng(_h("common", s)).standard_normal() for s in seeds])
        f = f_true(self.kind, design)
        hot = (design["k"] == "b") if self.kind == "hedge" else bump(design) >= 0.1 * A

        def unit(name: str, mean: float, starts: int) -> np.ndarray:
            idio = np.array([np.random.default_rng(_h(name, s)).standard_normal(starts) for s in seeds]).T
            return mean + 0.3 * common[None, :] + SIGMA * idio

        def arm(name: str, mean: float, starts: int = STARTS) -> dict[str, np.ndarray]:
            risk = 0.5 + 0.1 * unit("risk" + name, 0.0, starts)
            if self.kind == "limit" and name == did and bump(design) >= 0.3 * A:
                risk = risk + 1.0
            low = self.kind == "gated" and name == did and hot
            return {"money": unit(name, mean, starts), "risk": risk,
                    "supply": np.full((starts, len(seeds)), 0.0 if low else 1.0)}

        arms = {SV.DESIGN_ARM: arm(did, f)}
        nb = STARTS - 1 if self.kind == "unpaired" else STARTS
        for b in SV.BASELINES:
            arms[b] = arm(b, (A + 0.5) if (self.kind == "strong" and b == "p16") else 0.0, nb)
        money = arms[SV.DESIGN_ARM]["money"]
        traded = money - 3.0 if (self.kind == "harm" and hot) else money
        real = {SV.AS_TRADED: {"money": traded}, SV.REFLECTED: {"money": money}}
        side = "coin" if (self.kind == "coin_side" and hot) else SV.TRIGGER
        pos = [C.Position("topstep", "a1", 0, 10, 20, 1, ref=f"{did}/1")]
        if self.kind == "hedge" and hot:
            pos.append(C.Position("topstep", "a2", 0, 12, 18, -1, ref=f"{did}/2"))
        return SV.RunOutput(arms=arms, real_path=real, side_source=side, positions=tuple(pos), seeds=tuple(seeds),
                            blocks=tuple(tuple(b) for b in (self.blocks or protocol.blocks)),
                            horizon=protocol.horizon if self.horizon is None else self.horizon, tag=self.tag)

    def gate(self, out: Any) -> str | None:
        from extended import survey as SV

        s = float(np.mean(out.arms[SV.DESIGN_ARM]["supply"]))
        return f"supply {s:.2f} below 0.5 a session" if s < 0.5 else None


SPEC: dict[str, Any] = {
    "prereg_id": "F-99",
    "survey": {"n": 32, "method": "sobol", "seed": 11, "max_proposals": 2048},
    "rounds": {"count": 2, "seed": 12, "batch": 4, "pool": 256, "acquisition": "ei", "kappa": 2.0, "xi": 0.0,
               "centres": 2, "local": 16, "local_scale": 0.05, "restarts": 2, "p_feasible": 0.5},
    "protocol": {"measure": "composite", "blocks": [["2020-01-02", "2021-12-31"], ["2022-01-03", "2023-12-29"]],
                 "seeds": [101, 102, 103, 104], "horizon": 0},
    "composite": {"dims": [{"key": "money", "lo": -2.0, "hi": 4.0, "direction": 1, "weight": 1.0}]},
    "limits": {"list": [{"measure": "risk", "key": "risk", "bound": 1.0, "direction": "<="}], "check_level": 0.05},
    "baselines": {"names": ["naive_coin", "p14", "p15", "p16"], "seed": 13},
    "finalists": {"candidates": 3, "reread_seeds": list(range(201, 233)), "margin": 0.1, "z": 3.0},
    "no_harm": {"margin": 0.05},
    "plateau": {"rule": {"steps": {"x": 0.1, "y": 2, "k": "cells"}, "radius": 1, "tolerance_se": 2.5,
                         "margin": 0.1, "side": "worse", "min_share": 1.0, "min_neighbours": 3, "min_per_lever": 1},
                "seed": 14, "box_seed": None},
    "parts": {},
}


def spec(bound: Mapping[str, Any], **over: Any) -> dict[str, Any]:
    s = copy.deepcopy(SPEC)
    s["parts"] = copy.deepcopy(dict(bound))
    for k, v in over.items():
        s[k] = v
    return s


def declaration(s: Mapping[str, Any]) -> str:
    body = json.dumps(s, indent=2, sort_keys=True)
    return ("# F-99: the survey runner's synthetic search (a test fixture, never pinned)\n\n"
            "## 6. The survey, the surrogate and the rounds\n\n"
            f"```survey-spec\n{body}\n```\n")
