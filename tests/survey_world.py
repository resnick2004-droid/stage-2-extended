"""The Wave 5 survey runner's synthetic world (no bar, no result file of the repository, no held-out calendar):
imported by `tests/test_survey.py`, and named by its declarations as factory ids (`survey_world:make_runner` ...),
which the survey builds itself from their declared parameters (F-2). A test fixture pin only: under a real pin a part
is `extended.`'s.

**W42-R1 as it stands** (C-1): `load_w42()` reads `extended/wave42.py`, `scripts/wave42_apply.py` and the rule text
unedited from `WAVE42_COMMIT` on `wt/wt-infra` (`git show`) into a temporary root whose `extended/` is put on
`extended.__path__`. Its two calendar shas, not yet pinned there (`SEARCH_CALENDAR_SHA256` is None until Q-197; the
held-out calendar is never read here), are set to this world's synthetic calendars. Three **labelled stand-ins**, each
removed when its item lands:
* `W42_PUBLIC_STANDIN`: `composite_per_seed(values, sessions_left, out)` and `limit_estimate(values, sessions_left,
  out, name)`, the public functions the W42-R1 worker is adding (those `setting_rule` calls); attached only when the
  module lacks them, and checked by `tests/test_survey.py` to reproduce `setting_rule`'s own baseline composites,
  limit estimates and do-nothing floor on this world's H4 reading;
* `extended/search_calendar.py` (Q-197's loader, `load_search_calendar(path)`), written into the temporary root;
* `q192b_protocol_for`: Q-192b's change (the ledger reads a declared limit measure on the re-read seeds), asserting
  the real `protocol_for`'s signature first.

**The fixture** is W42-R1's own application: `w42_root(path, spread, base_q)` writes a synthetic H4 collection result
and sidecar, the two synthetic calendars, and runs `wave42_apply.apply` with synthetic `Sources` (the adapter returns
this world's baselines on every calendar session, seeds 0..15), so `results/w42_r1_values.csv` and its manifest are
the real format.

**The parts**: `make_space`, `make_gate`, `make_schedule`, `make_runner`, `make_playbook`. The runner's per-unit
latent is u = q(design) + 0.3 common(seed) + SIGMA idio(start, seed); every W42-R1 key moves with u and its own noise.
It reports six starts on the calendar (`STARTS`), never their sessions left. Its kinds, beside ``plateau``,
``spike``, ``noise``: ``near`` (the bump at `A_NEAR`), ``strong`` (P-16 above every design), ``ceiling`` (accounts at
once raised there), ``floor`` (trades taken lowered there), ``risky`` (the floor crossed on the fresh seeds only),
``tail`` (accounts at once heavy-tailed there: its p90 crosses, its mean does not), ``censor`` (trades taken zero on
the starts incomplete over W), ``harm`` and ``mixed`` (the as-traded side worse), ``coin_side``, ``hedge``,
``overlap``, ``gated``, ``nothing`` (W42-R1's do-nothing journey there), ``meagre`` (a paid, cheap, poor journey: only
the do-nothing floor fails), ``unpaid`` (good but never paid: only `not_paid_within_B` fails), ``unpaired``,
``realkeys``, ``range`` (a share above one), ``data`` (a data file read and not declared), ``offcal`` (a start off the
calendar). `CALLS` logs every design run.

The seeds here are small literals of these tests' own; none is a declared block.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import inspect
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping

import numpy as np

from extended import ROOT

WAVE42_COMMIT = "34ee968"          # wt/wt-infra: W42-R1 after its two corrective cycles (C-1)
A = 2.0
A_NEAR = 0.45                      # on the spread fixture: a gap past delta*, short of delta* + t se
A_NEAR6 = 1.1                      # at 6 re-read seeds: every t past the normal 3, one short of t(5)'s 5.51
SIGMA = 0.5
NO_HARM_MARGIN = 0.005
BASELINES = ("naive_coin", "p14", "p15", "p16")
N_CAL = 400                        # the synthetic search calendar's sessions, 2020-01-02 .. 2023-12-29
H4_SEEDS = 16
STARTS_LEFT = (320, 280, 240, 180, 130, 90)            # the runner's starts by sessions left: E_252 2, E_126 5, E_63 6
CALLS: list[str] = []
GATE_SEEN: list[tuple[str, ...]] = []
_W42: Any = None


def calendar() -> tuple[str, ...]:
    d0, d1 = np.datetime64("2020-01-02"), np.datetime64("2023-12-29")
    span = int((d1 - d0) / np.timedelta64(1, "D"))
    days = sorted({int(round(i * span / (N_CAL - 1))) for i in range(N_CAL)})
    assert len(days) == N_CAL
    return tuple(str(d0 + np.timedelta64(k, "D")) for k in days)


def held_out_calendar() -> tuple[str, ...]:
    d0 = np.datetime64("2024-01-02")
    return tuple(str(d0 + np.timedelta64(k, "D")) for k in range(0, 900, 2))


def _csv(dates) -> bytes:
    return ("date\n" + "".join(f"{d}\n" for d in dates)).encode("utf-8")


CAL = calendar()
STARTS = tuple(CAL[N_CAL - s] for s in STARTS_LEFT)

_CAL_LOADER = '''"""STAND-IN for Q-197's search calendar loader (tests/survey_world.py writes it; removed when Q-197 lands)."""
import csv, hashlib, io
from pathlib import Path
from types import SimpleNamespace


def load_search_calendar(path):
    raw = Path(path).read_bytes()
    dates = tuple(r["date"] for r in csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    return SimpleNamespace(dates=dates, file_sha256=hashlib.sha256(raw).hexdigest(),
                           calendar_sha256=hashlib.sha256("".join(f"{d}\\n" for d in dates).encode()).hexdigest())
'''


def load_w42():
    """W42-R1's module and application script, unedited from `WAVE42_COMMIT` (or this tree once merged), the stand-ins
    attached (the module docstring). Returns (wave42, wave42_apply)."""
    global _W42
    if _W42 is not None:
        return _W42
    import extended

    root = Path(tempfile.mkdtemp(prefix="survey-w42-"))
    for rel in ("extended/wave42.py", "scripts/wave42_apply.py", "docs/plans/WAVE42_SETTING_RULE.md"):
        mine = ROOT / rel
        if mine.is_file() and rel != "scripts/wave42_apply.py":
            data = mine.read_bytes()
        else:
            r = subprocess.run(["git", "show", f"{WAVE42_COMMIT}:{rel}"], cwd=ROOT, capture_output=True)
            if r.returncode != 0:
                import pytest
                pytest.skip(f"W42-R1's {rel} is neither in this tree nor at {WAVE42_COMMIT}")
            data = r.stdout
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(data)
    if not (ROOT / "extended" / "search_calendar.py").is_file():
        (root / "extended" / "search_calendar.py").write_text(_CAL_LOADER, encoding="utf-8")
    if not (ROOT / "extended" / "wave42.py").is_file() or not (ROOT / "extended" / "search_calendar.py").is_file():
        extended.__path__.append(str(root / "extended"))
    W = importlib.import_module("extended.wave42")
    W.SEARCH_CALENDAR_SHA256 = hashlib.sha256(_csv(CAL)).hexdigest()
    W.HELD_OUT_CALENDAR_SHA256 = hashlib.sha256(_csv(held_out_calendar())).hexdigest()
    for name, fn in W42_PUBLIC_STANDIN.items():
        if not hasattr(W, name):
            setattr(W, name, fn)
    spec = importlib.util.spec_from_file_location("wave42_apply", root / "scripts" / "wave42_apply.py")
    apply = importlib.util.module_from_spec(spec)
    sys.modules["wave42_apply"] = apply
    spec.loader.exec_module(apply)
    _W42 = (W, apply)
    return _W42


# ------------------------------------------------------------------------------------------------ the stand-ins


def _composite_standin(values, sessions_left, out):
    """STAND-IN for wave42.composite_per_seed (the W42-R1 worker's public function): setting_rule's composite, B-5 and
    all, on one arm -- C(c) = sum_k w_k mean_{s in E_k} z_k(s, c), cost's z 0 for a unit not passed by W."""
    W = _W42[0] if _W42 else importlib.import_module("extended.wave42")
    sl = np.asarray(sessions_left)
    per = {k: np.asarray(v, float) for k, v in out.items()}
    per.update(W.bankroll_states(per, values["budgets"]["primary"]))
    caps = {r["name"]: (r["lo"], r["hi"]) for r in values["dimensions"]}
    c = 0.0
    for d in W.DIMENSIONS:
        if d.name not in values["weights"]:
            continue
        lo, hi = caps[d.name]
        z = W._z(d, per[d.key], lo, hi)
        if d.name == "cost":
            z = np.where(per["first_pass_days"] <= W.W, z, 0.0)
        c = c + values["weights"][d.name] * z[W._rows(sl, d.horizon)].mean(axis=0)
    return np.asarray(c, float)


def _limit_standin(values, sessions_left, out, name):
    """STAND-IN for wave42.limit_estimate: setting_rule's estimate of a limit -- its statistic over its complete starts,
    pooled over seeds."""
    W = _W42[0] if _W42 else importlib.import_module("extended.wave42")
    L = next(x for x in W.LIMITS if x.name == name)
    per = {k: np.asarray(v, float) for k, v in out.items()}
    per.update(W.bankroll_states(per, values["budgets"]["primary"]))
    return W._stat(per[L.key][W._rows(np.asarray(sessions_left), L.horizon)], L.stat)


W42_PUBLIC_STANDIN = {"composite_per_seed": _composite_standin, "limit_estimate": _limit_standin}


def q192b_protocol_for(orig):
    """STAND-IN for Q-192b: `protocol_for(measure, reread=True)` admits a declared limit measure on the re-read seeds.
    It asserts the real method's signature first, so a changed API fails here, not silently."""
    sig = inspect.signature(orig)
    assert list(sig.parameters) == ["self", "measure", "reread"] and \
        sig.parameters["reread"].kind is inspect.Parameter.KEYWORD_ONLY, f"protocol_for's API changed: {sig}"

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
         ("n1", "n2", "n3", "p1", "p2", "p3", "spent", "pass", "pay", "cash", "oop", "steady", "taken", "accounts",
          "orders")}
    x = extra or {}
    v = {f"net_month_{m}": u + 0.8 * e[f"n{m}"] for m in (1, 2, 3)}
    v.update({f"peak_month_{m}": 100.0 + 20.0 * np.abs(e[f"p{m}"]) for m in (1, 2, 3)})
    v["spent_before_first_payout"] = np.maximum(0.0, 300.0 - 80.0 * u + 60.0 * e["spent"])
    v["first_pass_days"] = np.clip(40.0 - 12.0 * u + 10.0 * e["pass"], 0.0, 127.0)
    v["first_payout_days"] = np.minimum(127.0, v["first_pass_days"] + 10.0 + 15.0 * np.abs(e["pay"]))
    v["cash_to_first_pass"] = np.maximum(0.0, 200.0 - 40.0 * u + 40.0 * e["cash"])
    v["peak_oop_12_months"] = np.maximum(0.0, 800.0 - 150.0 * u + 120.0 * e["oop"])
    v["share_months_positive"] = np.clip(0.5 + 0.12 * u + 0.1 * e["steady"] - x.get("steady", 0.0), 0.0, 1.0)
    v["taken_mean"] = np.maximum(0.0, 5.0 + u + 0.8 * e["taken"] - x.get("taken", 0.0))
    v["accounts_max"] = np.maximum(0.0, 3.0 - 0.5 * u + 0.5 * e["accounts"] + x.get("accounts", 0.0))
    v["orders_max"] = np.maximum(0.0, 4.0 - 0.5 * u + 0.5 * e["orders"])
    return v


def nothing_values(seeds, starts: int, fee_unit: float) -> dict[str, np.ndarray]:
    """W42-R1's own do-nothing journey on every unit, the workload keys at zero."""
    W = load_w42()[0]
    z = np.zeros((starts, len(seeds)))
    v = {k: np.full_like(z, float(x)) for k, x in W.null_journeys(fee_unit)["do_nothing"].items()}
    for k in W.REQUIRED:
        v.setdefault(k, z.copy())
    return v


def baseline_values(seeds, starts: int, spread: float = 0.0, base_q: float = 0.0) -> dict[str, dict[str, np.ndarray]]:
    return {b: unit_values(b, base_q + spread * i, seeds, starts) for i, b in enumerate(BASELINES)}


def _manifest_writer(df, name, *, script, seed, parameters, results_dir, description="", require_seed=True, **kw):
    """`write_result`'s signature, writing the vendored manifest's fields (the CSV's raw-bytes sha256)."""
    d = Path(results_dir)
    p = d / (name if name.endswith(".csv") else f"{name}.csv")
    p.write_bytes(df.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    man = {"result_file": p.name, "script": script, "git_commit": "fixture", "seed": seed, "parameters": parameters,
           "timestamp": "fixture", "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "rows": int(len(df)),
           "columns": list(df.columns), "description": description}
    Path(f"{p}.manifest.json").write_text(json.dumps(man, sort_keys=True, indent=1), encoding="utf-8")
    return p, Path(f"{p}.manifest.json")


def w42_root(root: Path, spread: float = 0.0, base_q: float = 0.0) -> dict[str, Any]:
    """A repository root holding W42-R1's real output on this world's H4 reading (the module docstring); returns the
    values, the readings and their sessions left."""
    W, apply = load_w42()
    res = root / "results"
    res.mkdir(parents=True, exist_ok=True)
    (res / W.SEARCH_CALENDAR).write_bytes(_csv(CAL))
    (res / W.HELD_OUT_CALENDAR).write_bytes(_csv(held_out_calendar()))
    seeds = tuple(range(H4_SEEDS))
    vals = baseline_values(seeds, N_CAL, spread, base_q)
    readings = {b: W.BaselineReading(b, W.BLOCK, W.READING, CAL, seeds, vals[b]) for b in BASELINES}
    coll = res / W.COLLECTION_RESULT
    coll.write_bytes(b"synthetic,h4\n1,1\n")
    man = {"sha256": hashlib.sha256(coll.read_bytes()).hexdigest(), "parameters": {
        "block": W.BLOCK, "reading": W.READING, "arm": W.ARM, **W.VERDICT, "W": W.W, "baselines": list(BASELINES),
        "starts": list(CAL), "seeds": list(seeds), "calendar_sha256": W.calendar_digest(CAL),
        "readings_sha256": W.readings_digest(readings)}}
    Path(f"{coll}.manifest.json").write_text(json.dumps(man), encoding="utf-8")
    loader = importlib.import_module("extended.search_calendar").load_search_calendar
    src = apply.Sources(adapter=lambda path, sidecar: readings, calendar_loader=loader,
                        fee=lambda: (50.0, W.FEE_SOURCE, "0" * 64), writer=_manifest_writer)
    apply.apply(res, src)
    out = root / "results" / W.OUTPUT_NAME
    import csv as _csv_mod
    import io
    values = {r["key"]: json.loads(r["value_json"]) for r in
              _csv_mod.DictReader(io.StringIO(out.read_text(encoding="utf-8")))}
    (root / "DECISIONS.md").write_text("| id | date | decision | basis |\n|---|---|---|---|\n", encoding="utf-8")
    return {"values": values, "readings": vals, "sl": np.array([N_CAL - i for i in range(N_CAL)]),
            "values_sha256": hashlib.sha256(out.read_bytes()).hexdigest()}


# ------------------------------------------------------------------------------------------------ the parts


def make_space(x_hi: float = 1.0, extra: list | None = None):
    from extended import search_space as SS

    dims = [SS.Dim("x", SS.REAL, lo=0.0, hi=float(x_hi), step=0.1, lever="S1"),
            SS.Dim("y", SS.INT, lo=0, hi=20, step=2, lever="T3"),
            SS.Dim("k", SS.CAT, values=("a", "b"), lever="T5")]
    for d in extra or []:
        dims.append(SS.Dim(d["name"], SS.CAT, values=tuple(d["values"]), lever=d.get("lever", "")))
    return SS.Space(tuple(dims), fixed={"overlap": "refused"})


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


def q_of(kind: str, d: Mapping[str, Any], a_near: float) -> float:
    if kind == "spike":
        return A if abs(d["x"] - 0.3) < 1e-9 else 0.0
    if kind == "noise":
        return 0.0
    if kind == "near":
        return bump(d, a_near)
    if kind == "hedge":
        return bump(d) if d["k"] == "b" else 0.0
    return bump(d)


def make_runner(kind: str = "plateau", tag: str = "search", blocks: list | None = None, horizon: int | None = None,
                shift: float = 0.0, harm: float = 0.0, steady_weight: float = 1.0, hot_tag: str | None = None,
                base_q: float = 0.0, a_near: float = A_NEAR, meagre: dict | None = None, fee_unit: float = 50.0,
                late_start: str | None = None):
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
        n = len(STARTS)
        q = q_of(kind, design, a_near) + float(shift) + float(base_q)
        if kind == "mixed" and design["k"] == "b":
            q += 0.5 * bump(design)
        if kind == "nothing" and hot:
            arm = nothing_values(seeds, n, fee_unit)
        elif kind == "meagre" and hot:
            arm = {k: np.full((n, len(seeds)), float(meagre[k])) for k in meagre}
        else:
            arm = unit_values(did, q, seeds, n, extra=extra)
        if kind == "unpaid" and hot:
            arm["first_payout_days"] = np.full_like(arm["first_payout_days"], 127.0)
        if kind == "tail" and hot:
            pick = (np.arange(arm["accounts_max"].size).reshape(arm["accounts_max"].shape) % 5) == 0   # a fifth
            arm["accounts_max"] = np.where(pick, 8.0, np.minimum(arm["accounts_max"], 2.5))
        if kind == "censor" and hot:
            arm["taken_mean"] = np.where(np.asarray(STARTS_LEFT)[:, None] < 126, 0.0, arm["taken_mean"])
        if kind == "range" and hot:
            arm["share_months_positive"] = np.full_like(arm["share_months_positive"], 1.5)
        arm["supply"] = np.full((n, len(seeds)), 0.0 if (kind == "gated" and hot) else 1.0)
        arms = {SV.DESIGN_ARM: arm}
        nb = n - 1 if kind == "unpaired" else n
        for b in SV.BASELINES:
            arms[b] = unit_values(b, ((A + 1.0) if (kind == "strong" and b == "p16") else 0.0) + float(base_q),
                                  seeds, nb)
        refl = {k: v for k, v in arm.items() if k != "supply"}
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
        starts = list(STARTS)
        if kind == "offcal" and hot:
            starts[0] = "2020-01-03" if "2020-01-03" not in CAL else "2020-01-04"
        if late_start:
            starts[-1] = late_start
        data = {"results/undeclared.csv": "0" * 64} if (kind == "data" and hot) else {}
        return SV.RunOutput(starts=tuple(starts), arms=arms, real_path=real, side_source=side, positions=pos,
                            data=data, seeds=tuple(seeds), blocks=tuple(tuple(b) for b in (blocks or protocol.blocks)),
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
    "no_harm": {"margin": NO_HARM_MARGIN, "margin_row": "fixture"},
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


def spec(parts_block: Mapping[str, Any], *, protocol_sha256: str, code_sha256: str, values_row: str = "fixture",
         **over: Any) -> dict[str, Any]:
    s = copy.deepcopy(SPEC)
    s["parts"] = copy.deepcopy(dict(parts_block))
    s["objective"] = {"rule_id": "W42-R1", "values_row": values_row, "code_sha256": code_sha256}
    for k, v in over.items():
        s[k] = copy.deepcopy(v)
    s["protocol"] = dict(s["protocol"], sha256=protocol_sha256)
    return s


def declaration(s: Mapping[str, Any]) -> str:
    body = json.dumps(s, indent=2, sort_keys=True)
    return ("# F-99: the survey runner's synthetic search (a test fixture, never pinned)\n\n"
            "## 6. The survey, the surrogate and the rounds\n\n"
            f"```survey-spec\n{body}\n```\n")
