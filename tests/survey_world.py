"""The Wave 5 survey runner's synthetic world (no bar, no result file of the repository): imported by
`tests/test_survey.py`, and named by its declarations as factory ids (`survey_world:make_runner` ...), which the survey
builds itself from their declared parameters (F-2). A test fixture pin only: under a real pin a part is `extended.`'s.

* `load_wave42()`: W42-R1's module (`extended/wave42.py`), from this tree when it holds it, else read unedited from
  `WAVE42_COMMIT` on `wt/wt-infra` (`git show`) into a temporary folder put on `extended.__path__`.
* `q192(SS)`: Q-192's engine change as the survey builds to it (F-3) -- the ledger reads a declared limit measure on the
  re-read seeds -- for `monkeypatch` (a stand-in until Q-192 merges; the survey refuses an engine without it).
* `w42_fixture(path, spread)`: an H4-shaped reading of the four baselines (`baseline_values`, their qualities
  `spread` apart), W42-R1's `setting_rule` run on
  it, the no-harm margin added (`NO_HARM_MARGIN`; the interface W42-R1's re-declaration is assumed to carry), written as
  canonical JSON; returns its values.
* `make_space`, `make_gate`, `make_schedule`, `make_runner`, `make_playbook`: the parts' factories. The runner's
  per-unit latent is u = q(design) + 0.3 common(seed) + SIGMA idio(start, seed); every W42-R1 key moves with u and its
  own noise. Every design it runs is logged in `CALLS`. Its kinds:
  - ``plateau`` (a broad bump of height `A` at x 0.7, y 12), ``spike`` (`A` at x = 0.3 only), ``noise`` (q = 0),
    ``near`` (the bump at `A_NEAR`: its composite gain past delta*, short of delta* plus the t threshold),
    ``strong`` (P-16 at `A` + 1 everywhere), ``ceiling`` (the bump; its accounts at once raised there, a p90
    ceiling crossed), ``floor`` (its trades taken lowered there, a p10 floor crossed), ``risky`` (the floor crossed
    on the fresh seeds only: lucky on the selection seeds, the note's winner's curse), ``harm`` (its as-traded
    `share_months_positive` lowered there by `harm` / the steady weight), ``coin_side``, ``hedge`` (opposite
    positions on two accounts, k = b only, the bump on k = b only), ``overlap`` (two same-side positions at once),
    ``gated`` (its supply 0 there), ``nothing`` (the region buys nothing: `nothing_values`), ``mixed`` (the bump on
    both cells of k, half again higher on k = b, whose as-traded side harms), ``unpaired`` (the baselines on one start fewer), ``realkeys`` (a third real-path
    reading).
  `tag`, `blocks`, `horizon` override the report (held-out); `shift` adds to every design's q (a runner setting).
* `spec(...)`, `declaration(spec)`: the tests' declared numbers with the parts bound.

The seeds here are small literals of these tests' own; none is a declared block.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from extended import ROOT

WAVE42_COMMIT = "856c9bb"          # wt/wt-infra: extended/wave42.py, identical to 2bde318 (W42-R1 under review)
A = 2.0
A_NEAR = 0.48                      # on the spread fixture (delta* 0.06): a gap past delta*, short of its t
SIGMA = 0.5
SESSIONS_LEFT = (320, 280, 240, 180, 130, 90)          # E_252: 2 starts, E_126: 5, E_63: 6
NO_HARM_MARGIN = 0.005
BASELINES = ("naive_coin", "p14", "p15", "p16")
CALLS: list[str] = []
_W42: Any = None


def load_wave42():
    global _W42
    if _W42 is not None:
        return _W42
    import importlib

    import extended

    if not (ROOT / "extended" / "wave42.py").is_file():
        r = subprocess.run(["git", "show", f"{WAVE42_COMMIT}:extended/wave42.py"], cwd=ROOT, capture_output=True)
        if r.returncode != 0:
            import pytest
            pytest.skip(f"W42-R1's module is neither in this tree nor at {WAVE42_COMMIT}")
        tmp = Path(tempfile.mkdtemp(prefix="survey-w42-"))
        (tmp / "wave42.py").write_bytes(r.stdout.replace(b"\r\n", b"\n"))
        extended.__path__.append(str(tmp))
    _W42 = importlib.import_module("extended.wave42")
    return _W42


def q192_protocol_for(orig):
    """The ledger's `protocol_for` with Q-192's change: a declared limit measure on the re-read seeds."""
    def protocol_for(self, measure=None, *, reread=False):
        if reread and measure is not None and measure in self.measures:
            return self.reread.with_measure(measure)
        return orig(self, measure, reread=reread)
    return protocol_for


# ------------------------------------------------------------------------------------------------ the units


def _h(*parts: Any) -> int:
    return int(hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:15], 16)


def _noise(name: str, seeds, starts: int) -> np.ndarray:
    return np.array([np.random.default_rng(_h(name, int(s))).standard_normal(starts) for s in seeds]).T


def unit_values(name: str, q: float, seeds, starts: int, *, extra: Mapping[str, float] | None = None
                ) -> dict[str, np.ndarray]:
    """Every W42-R1 key of one arm, start by seed, from its latent u = q + 0.3 common + SIGMA idio."""
    common = np.array([np.random.default_rng(_h("common", int(s))).standard_normal() for s in seeds])
    u = q + 0.3 * common[None, :] + SIGMA * _noise(name, seeds, starts)
    e = {k: _noise(f"{name}/{k}", seeds, starts) for k in
         ("n1", "n2", "n3", "p1", "p2", "p3", "spent", "days", "cash", "oop", "steady", "taken", "accounts")}
    x = extra or {}
    v = {f"net_month_{m}": u + 0.8 * e[f"n{m}"] for m in (1, 2, 3)}
    v.update({f"peak_month_{m}": 100.0 + 20.0 * np.abs(e[f"p{m}"]) for m in (1, 2, 3)})
    v["spent_before_first_payout"] = np.maximum(0.0, 300.0 - 80.0 * u + 60.0 * e["spent"])
    v["first_payout_days"] = np.clip(60.0 - 15.0 * u + 12.0 * e["days"], 0.0, 127.0)
    v["cash_to_first_pass"] = np.maximum(0.0, 200.0 - 40.0 * u + 40.0 * e["cash"])
    v["peak_oop_12_months"] = np.maximum(0.0, 800.0 - 150.0 * u + 120.0 * e["oop"])
    v["share_months_positive"] = np.clip(0.5 + 0.12 * u + 0.1 * e["steady"] - x.get("steady", 0.0), 0.0, 1.0)
    v["taken_mean"] = np.maximum(0.0, 5.0 + u + 0.8 * e["taken"] - x.get("taken", 0.0))
    v["accounts_max"] = np.maximum(0.0, 3.0 - 0.5 * u + 0.5 * e["accounts"] + x.get("accounts", 0.0))
    return v


def baseline_values(seeds, starts: int, spread: float = 0.0, base_q: float = 0.0) -> dict[str, dict[str, np.ndarray]]:
    return {b: unit_values(b, base_q + spread * i, seeds, starts) for i, b in enumerate(BASELINES)}


def nothing_values(seeds, starts: int) -> dict[str, np.ndarray]:
    """The design that buys nothing: no evaluation, no spend, no payout, every month flat (V-4)."""
    z = np.zeros((starts, len(seeds)))
    v = {f"net_month_{m}": z.copy() for m in (1, 2, 3)}
    v.update({f"peak_month_{m}": z.copy() for m in (1, 2, 3)})
    v.update(spent_before_first_payout=z.copy(), first_payout_days=np.full_like(z, 127.0), cash_to_first_pass=z.copy(),
             peak_oop_12_months=z.copy(), share_months_positive=z.copy(), taken_mean=z.copy(), accounts_max=z.copy())
    return v


def do_nothing_composite(W, v: Mapping[str, Any], sl) -> float:
    """W42-R1's composite of the do-nothing design, by its own pieces (`_derived`, `_rows`, `_z`), on `sl`."""
    seeds = range(2)
    arm = nothing_values(seeds, len(sl))
    per = dict(arm)
    per.update(W._derived(arm, v["budgets"]["primary"]))
    by = {d.name: d for d in W.DIMENSIONS}
    c = 0.0
    for d in v["dimensions"]:
        if d["name"] in v["weights"]:
            rows = W._rows(np.asarray(sl), by[d["name"]].horizon)
            c += v["weights"][d["name"]] * float(W._z(by[d["name"]], per[d["key"]][rows], d["lo"], d["hi"]).mean())
    return c


def w42_fixture(path: Path, spread: float = 0.0, base_q: float = 0.0) -> dict[str, Any]:
    """H4's shape on the toy baselines, W42-R1's own rule on it, the no-harm margin beside; canonical JSON at path."""
    W = load_wave42()
    n, seeds = 40, list(range(901, 917))
    sl = tuple(range(420, 420 - 10 * n, -10))
    days = [str(np.datetime64("2020-01-06") + np.timedelta64(7 * i, "D")) for i in range(n)]
    vals = baseline_values(seeds, n, spread, base_q)
    rs = {b: W.BaselineReading(b, "search", tuple(days), sl, tuple(seeds), vals[b]) for b in BASELINES}
    v = dict(W.setting_rule(rs, fee_unit=50.0, fee_source="the tests' fixture", test_starts={63: 100, 126: 80,
                                                                                               252: 50},
                            test_seeds=64).values)
    v["no_harm"] = {"margin": NO_HARM_MARGIN, "source": "the tests' fixture (the assumed W42-R1 interface)"}
    v["do_nothing"] = {"composite": do_nothing_composite(W, v, sl),
                       "source": "the tests' fixture: W42-R1's pieces on the design that buys nothing (V-4)"}
    path.write_bytes(json.dumps(v, sort_keys=True, separators=(",", ":"), default=float).encode("utf-8"))
    return v


# ------------------------------------------------------------------------------------------------ the parts


def make_space(x_hi: float = 1.0, extra: list | None = None):
    from extended import search_space as SS

    dims = [SS.Dim("x", SS.REAL, lo=0.0, hi=float(x_hi), step=0.1, lever="S1"),
            SS.Dim("y", SS.INT, lo=0, hi=20, step=2, lever="T3"),
            SS.Dim("k", SS.CAT, values=("a", "b"), lever="T5")]
    for d in extra or []:
        dims.append(SS.Dim(d["name"], SS.CAT, values=tuple(d["values"]), lever=d.get("lever", "")))
    return SS.Space(tuple(dims), fixed={"overlap": "refused"})


GATE_SEEN: list[tuple[str, ...]] = []


def make_gate(floor: float = 0.5, key: str = "supply"):
    def gate(view):
        GATE_SEEN.append(tuple(sorted(view)))
        s = float(np.mean(view[key]))
        return f"{key} {s:.2f} below {floor}" if s < floor else None
    return gate


def make_schedule():
    def build(design):
        return ("toy-schedule", json.dumps(dict(design), sort_keys=True))
    return build


def make_playbook(style: str = "plain"):
    def playbook(design):
        return (f"# Playbook ({style})\n\nLevers: {json.dumps(dict(design), sort_keys=True)}\n"
                "Side: each trade's side is its own trigger's; no two accounts on opposite sides at once.\n")
    return playbook


def bump(d: Mapping[str, Any], height: float = A) -> float:
    return height * float(np.exp(-((d["x"] - 0.7) / 0.3) ** 2 - ((d["y"] - 12) / 8.0) ** 2))


def q_of(kind: str, d: Mapping[str, Any]) -> float:
    if kind == "spike":
        return A if abs(d["x"] - 0.3) < 1e-9 else 0.0
    if kind == "noise":
        return 0.0
    if kind == "near":
        return bump(d, A_NEAR)
    if kind == "hedge":
        return bump(d) if d["k"] == "b" else 0.0
    return bump(d)


def make_runner(kind: str = "plateau", tag: str = "search", blocks: list | None = None, horizon: int | None = None,
                shift: float = 0.0, harm: float = 0.0, steady_weight: float = 1.0, hot_tag: str | None = None,
                base_q: float = 0.0):
    def runner(schedule, protocol):
        from extended import components as C
        from extended import search_space as SS
        from extended import survey as SV

        design = json.loads(schedule[1])
        did = SS.design_id(design)
        CALLS.append(did)
        seeds = protocol.seeds
        hot = (design["k"] == "b") if kind == "hedge" else bump(design) >= 0.1 * A
        if kind == "mixed":
            hot = hot and design["k"] == "b"
        fresh = min(seeds) >= 200
        extra = {}
        if kind == "ceiling" and hot:
            extra["accounts"] = 4.0
        if kind == "floor" and hot or kind == "risky" and hot and fresh:
            extra["taken"] = 6.0
        n = len(SESSIONS_LEFT)
        q = q_of(kind, design) + float(shift) + float(base_q)
        if kind == "mixed" and design["k"] == "b":
            q += 0.5 * bump(design)
        arms = {SV.DESIGN_ARM: nothing_values(seeds, n) if (kind == "nothing" and hot)
                else unit_values(did, q, seeds, n, extra=extra)}
        arms[SV.DESIGN_ARM]["supply"] = np.full((n, len(seeds)), 0.0 if (kind == "gated" and hot) else 1.0)
        nb = n - 1 if kind == "unpaired" else n
        for b in SV.BASELINES:
            arms[b] = unit_values(b, ((A + 1.0) if (kind == "strong" and b == "p16") else 0.0) + float(base_q),
                                  seeds, nb)
        refl = arms[SV.DESIGN_ARM]
        traded = dict(refl)
        if kind in ("harm", "mixed") and hot:
            traded["share_months_positive"] = np.clip(refl["share_months_positive"] - harm / steady_weight, 0.0, 1.0)
        real = {SV.AS_TRADED: traded, SV.REFLECTED: refl}
        if kind == "realkeys":
            real["mirror"] = refl
        side = "coin" if (kind == "coin_side" and hot) else SV.TRIGGER
        pos = {}
        for s in range(n):
            for c in seeds:
                p = [C.Position("topstep", "a1", s, 10, 20, 1, ref=f"{did}/s{s}c{c}/1")]
                if kind in ("hedge", "overlap") and hot and s == 0:
                    p.append(C.Position("topstep", "a2", s, 12, 18, -1 if kind == "hedge" else 1,
                                        ref=f"{did}/s{s}c{c}/2"))
                pos[f"s{s}c{c}"] = p
        return SV.RunOutput(arms=arms, sessions_left=SESSIONS_LEFT, real_path=real, side_source=side, positions=pos,
                            seeds=tuple(seeds), blocks=tuple(tuple(b) for b in (blocks or protocol.blocks)),
                            horizon=protocol.horizon if horizon is None else int(horizon),
                            tag=hot_tag if (hot_tag and hot) else tag)
    return runner


# ------------------------------------------------------------------------------------------------ the declaration


SPEC: dict[str, Any] = {
    "prereg_id": "F-99",
    "survey": {"n": 32, "method": "sobol", "seed": 11, "max_proposals": 2048},
    "rounds": {"count": 2, "seed": 12, "batch": 4, "pool": 256, "acquisition": "ei", "kappa": 2.0, "xi": 0.0,
               "centres": 2, "local": 16, "local_scale": 0.05, "restarts": 2, "p_feasible": 0.5},
    "protocol": {"measure": "composite", "blocks": [["2020-01-02", "2021-12-31"], ["2022-01-03", "2023-12-29"]],
                 "seeds": [101, 102, 103, 104], "horizon": 0},
    "baselines": {"names": list(BASELINES), "seed": 13},
    "finalists": {"candidates": 3, "reread_seeds": list(range(201, 233)), "z": 3.0},
    "plateau": {"rule": {"steps": {"x": 0.1, "y": 2, "k": "cells"}, "radius": 1, "tolerance_se": 2.5,
                         "margin": "delta_star", "side": "worse", "min_share": 1.0, "min_neighbours": 3,
                         "min_per_lever": 1}, "seed": 14, "box_seed": None},
}


def parts_of(kind: str = "plateau", *, runner: Mapping[str, Any] | None = None, gate: Mapping[str, Any] | None = None,
             space: Mapping[str, Any] | None = None, playbook: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"space": {"id": "survey_world:make_space", "params": dict(space or {})},
            "gate": {"id": "survey_world:make_gate", "params": dict(gate or {"floor": 0.5}), "keys": ["supply"]},
            "schedule_builder": {"id": "survey_world:make_schedule", "params": {}},
            "runner": {"id": "survey_world:make_runner", "params": dict(runner or {"kind": kind})},
            "playbook": {"id": "survey_world:make_playbook", "params": dict(playbook or {})}}


def spec(parts_block: Mapping[str, Any], objective: Mapping[str, Any], **over: Any) -> dict[str, Any]:
    s = copy.deepcopy(SPEC)
    s["parts"] = copy.deepcopy(dict(parts_block))
    s["objective"] = dict(objective)
    for k, v in over.items():
        s[k] = v
    return s


def declaration(s: Mapping[str, Any]) -> str:
    body = json.dumps(s, indent=2, sort_keys=True)
    return ("# F-99: the survey runner's synthetic search (a test fixture, never pinned)\n\n"
            "## 6. The survey, the surrogate and the rounds\n\n"
            f"```survey-spec\n{body}\n```\n")
