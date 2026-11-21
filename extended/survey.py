"""Wave 5 (the restart plan, Waves 5-6; CHARTER 3.3, 3.5, 3.6, 3.8, 3.9; the design-search template's sections 6, 7
and 14): the survey runner -- the end-to-end driver of one declared design search, on the search years only.

    from extended import survey as SV
    out = SV.run_survey("prereg/F-NN_<name>.md", results_dir=..., name="F-NN_survey")
    out.token          # "heldout-finalists: F-NN @ <declaration sha> list <list sha>", or None (no finalist)

**Nothing is injected** (the red team's F-2): the declaration names every part -- the lever space, the gate, the
schedule builder, the three-way runner and the playbook writer -- by a factory id (`module:function`) and its
parameters, and this module builds each part itself (`build_part`). Each part is **bound** by the sha256 of its id, its
canonical parameters and the code it runs: its module and every module of `extended/` it imports, transitively
(`code_closure`); the engine (Wave 3.4: `search_space`, `surrogate`, `proposer`, `plateau`) and the objective's code
(`extended.wave42`) are bound the same way. A binding that differs from the declaration's refuses (`PartRefused`).
Under a pin a part's module is this repository's (`extended.`), the tree is clean, and its commit is recorded.

**One objective** (F-1, F-11): the composite, its dimensions and every limit are W42-R1's, computed by
`extended.wave42`'s own functions (`_derived`, `_rows`, `_z`, `_stat`; its `DIMENSIONS` and `LIMITS`) from **its
pinned result file** (the declaration names the file and its sha256): each dimension averaged over the starts complete
for its own horizon (the runner reports each start's sessions left), each limit read as its declared statistic (a
quantile as a quantile) over its own complete starts, pooled over seeds. The weights, caps, budget B*, limits and their
check level, the size that matters (delta*) and the no-harm margin are read from that file; none is typed in the
declaration. The plateau rule's margin is the word ``delta_star``.

**Refusals first** (nothing is written by these): the declaration's bytes read once, hashed and parsed (n-3); its
`survey-spec` block exactly its form (`load_spec`; the four baselines, at least `MIN_REREAD_SEEDS` fresh re-read seeds,
z above zero); **pinned** in this repository's `DECISIONS.md` only (or a test's `fixture_pin`, outside `prereg/` and any
`results/`); every binding equal; every searched lever an id of `extended.lever_space`'s searched levers (an
allowlist, none of which sets a side: F-8); the engine able to read the declared limits on the re-read seeds (Q-192);
**not a second run** of this declaration (F-5: no output of the run's names in the folder, no variants row of this
declaration, no finalists' token for it in the decision log); the protocol refusing the held-out years.

**The loop** (each step a function, so a test can mutate it):
2. `draw_survey`: the survey declares the protocol, re-read seeds and limit measures to the one cell ledger;
3-5. `read_design`: the part-built schedule run through the runner; **`_check_output` refuses a held-out tag, block or
   horizon first** (F-4: the whole run refuses, before the book, the gate or any reading), then an off-protocol or
   unpaired report; `screen` -- one `components.UserBook` per (start, seed) path (n-a; tier 1 and overlap) and the
   gate on **only its declared keys** of the design's arm (F-10) -- refuses a design before any measure; then the
   composite and each limit through the door;
6. `run_rounds`: exactly the declared rounds;
7. `choose_finalists` (the finalist order rule): **the floors before ranking** (V-4, in order: the no-harm floor, the
   `not_paid_within_B` limit, the do-nothing floor -- the composite strictly above W42-R1's `do_nothing` composite,
   the design that buys nothing; a cell failing one is recorded with its candidates as rank 0, never ranked), then the
   cells left by selection reading, the first `candidates`;
   each re-read on the fresh seeds and kept only if (a) it beats **each** baseline by more than delta* at the declared z,
   read as a one-sided level and compared on the t law with n - 1 degrees of freedom (F-7); (b) **every limit's
   re-read point estimate** is inside its bound (F-3, E-230), the selection reading and the one-sided check (t law,
   W42's check level) beside; (c) the no-harm floor (the trigger's side; the as-traded composite no worse than the
   coin-side as-walked one, `REFLECTED`, by more than the margin); (d) the do-nothing floor again on the re-read;
   (e) the plateau (side ``worse`` only, n-c);
8. `emit`: the readings (the baselines' included, n-e), the candidates, the finalists' list (each with its bound
   playbook's text and sha256), then the variants rows (each carrying the declaration's and protocol's sha256); the
   token in Q-158's form. A refusal after the first cell writes the variants rows, then the failure record, each
   attempted whatever the other does (F-6), and is re-raised.
"""
from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
import json
import math
import re
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from extended import ROOT
from extended import reader as R

TASK = "Wave 5"
ENGINE_COMMIT = "df367a7"
W42_RULE = "W42-R1"
DESIGN_ARM = "design"
BASELINE_ROLE = "baseline"
BASELINES = ("naive_coin", "p14", "p15", "p16")       # CHARTER 2, 3.8 (b): Topstep's baseline set (E-221)
MIN_REREAD_SEEDS = 5                                    # the lead's floor (E-251)
AS_TRADED, REFLECTED = "as_traded", "reflected"
TRIGGER = "trigger"
SEARCH_TAG = "search"
DELTA_STAR = "delta_star"
SPEC_FENCE = re.compile(rb"^```survey-spec[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
FIXTURE_PREFIX = "survey-fixture-pin:"
SEARCH_DECLARATION = re.compile(r"prereg/F-\d+_[^/`]*\.md")
PART_NAMES = ("space", "gate", "schedule_builder", "runner", "playbook")
ENGINE_MODULES = ("extended.search_space", "extended.surrogate", "extended.proposer", "extended.plateau")
OUTPUTS = ("readings", "candidates", "finalists", "failure")
_HELD_OUT_WORDS = ("heldout", "judged", "holdout", "confirm")
_HELD_OUT_LABEL = re.compile(r"held[-_ ]?out|judged|confirmation", re.IGNORECASE)
_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

ROUND_KEYS = ("batch", "pool", "acquisition", "kappa", "xi", "centres", "local", "local_scale", "restarts",
              "p_feasible")
SPEC_KEYS: dict[str, tuple[str, ...] | None] = {
    "prereg_id": None,
    "survey": ("n", "method", "seed", "max_proposals"),
    "rounds": ("count", "seed") + ROUND_KEYS,
    "protocol": ("measure", "blocks", "seeds", "horizon"),
    "objective": ("rule_id", "file", "sha256", "code_sha256"),
    "baselines": ("names", "seed"),
    "finalists": ("candidates", "reread_seeds", "z"),
    "plateau": ("rule", "seed", "box_seed"),
    "parts": PART_NAMES + ("engine",),
}


class SurveyRefused(RuntimeError):
    """A survey this module cannot stand behind."""


class NotPinned(SurveyRefused):
    """The declaration is not pinned by a row of this repository's decision log (nor a test's fixture)."""


class SpecRefused(SurveyRefused):
    """The declaration's survey-spec block, or the objective's result file, is missing, malformed or off its form."""


class PartRefused(SurveyRefused):
    """A part whose binding differs from the declaration's, or a part the runner never accepts."""


class RunRepeated(SurveyRefused):
    """A second run of one declaration (F-5): results are never overwritten and a survey is run once."""


class HeldOutRow(SurveyRefused):
    """A variants row naming the held-out years or a held-out tag (CHARTER 3.3 (f))."""


class _Refused(Exception):
    """A design refused at its read, before any measure (the book or the gate): its cell stays counted."""

    def __init__(self, cls: str, reason: str):
        super().__init__(f"{cls}: {reason}")
        self.cls, self.reason = cls, reason


# ------------------------------------------------------------------------------------------------ what a run reports


@dataclass(frozen=True)
class RunOutput:
    """The three-way runner's report for one design on one protocol: `arms[arm][key]` a start-by-seed matrix for
    `DESIGN_ARM` and each baseline, on the same starts, for every key W42-R1 reads (its `REQUIRED`, and each optional
    key a limit reads) and the gate's keys; `sessions_left` each start's sessions left in its block (MEASURES 1.1, the
    dimension's complete starts); `real_path[AS_TRADED | REFLECTED][key]` the design's real-path readings --
    `AS_TRADED` its trigger's own sides, `REFLECTED` the coin side on the as-walked (reflected) path, same fills, same
    seeds (CHARTER 3.8's exception; n-b) -- never the deciding reading; `side_source` where the playbook's sides come
    from (`TRIGGER`); `positions[path]` every `components.Position` of one (start, seed) path, across the user's
    accounts and firms; the seeds, blocks and horizon it ran; its tag."""

    arms: Mapping[str, Mapping[str, Any]]
    sessions_left: tuple[int, ...]
    real_path: Mapping[str, Mapping[str, Any]]
    side_source: str
    positions: Mapping[str, Sequence[Any]]
    seeds: tuple[int, ...]
    blocks: tuple[tuple[str, str], ...]
    horizon: int
    tag: str = SEARCH_TAG


@dataclass(frozen=True)
class Engine:
    """Wave 3.4's engine modules: `search_space`, `proposer` (with its `surrogate`), `plateau`."""

    SS: Any
    P: Any
    PL: Any

    @classmethod
    def default(cls) -> "Engine":
        from extended import plateau, proposer, search_space
        return cls(search_space, proposer, plateau)

    def modules(self) -> dict[str, Any]:
        return {"search_space": self.SS, "surrogate": self.P.SG, "proposer": self.P, "plateau": self.PL}

    def check(self) -> None:
        """Refuse an engine without the API that stood (df367a7: the protocol is the ledger's)."""
        import inspect

        SS, PL = self.SS, self.PL
        for fn, names in ((SS.Sampler.survey, ("protocol", "reread_seeds", "measures")),
                          (SS.admit_one, ("measure", "reread")),
                          (SS.CellLedger.begin, ("protocol", "reread_seeds", "measures"))):
            if not all(n in inspect.signature(fn).parameters for n in names):
                raise PartRefused(f"the engine's {fn.__qualname__} lacks {names}: not the engine that stood "
                                  f"({ENGINE_COMMIT})")
        if "protocol" in inspect.signature(PL.check).parameters or not hasattr(SS.CellLedger, "protocol_for") \
                or "reads_through" in {f.name for f in fields(SS.Reading)}:
            raise PartRefused(f"the engine is not the one that stood ({ENGINE_COMMIT}): the doors take a caller's "
                              "protocol")


# ------------------------------------------------------------------------------------------------ bindings


def _lf_sha(p: Any) -> str:
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _digest(obj: Any) -> str:
    if is_dataclass(obj) and not isinstance(obj, type):
        obj = asdict(obj)
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _origin(name: str) -> str | None:
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return None
    return spec.origin if spec is not None and spec.origin and spec.origin.endswith(".py") else None


def _imports(path: str, name: str) -> set[str]:
    """The `extended` modules a file imports (absolute or relative), as module names."""
    tree = ast.parse(Path(path).read_bytes())
    pkg = name.rsplit(".", 1)[0] if not path.endswith("__init__.py") else name
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out |= {a.name for a in node.names if a.name.split(".")[0] == "extended"}
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = pkg.split(".")
                base = ".".join(parts[:len(parts) - node.level + 1] + ([node.module] if node.module else []))
            if base.split(".")[0] != "extended":
                continue
            out.add(base)
            out |= {f"{base}.{a.name}" for a in node.names if _origin(f"{base}.{a.name}")}
    return out


def code_closure(module: str) -> dict[str, str]:
    """{module: LF sha256 of its file} for `module` and every `extended` module it imports, transitively."""
    seen: dict[str, str] = {}
    todo = [module]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        src = _origin(name)
        if src is None:
            raise PartRefused(f"the module {name!r} has no source file to bind")
        seen[name] = _lf_sha(src)
        todo += sorted(_imports(src, name) - set(seen))
    return dict(sorted(seen.items()))


def _canon(x: Any) -> Any:
    if isinstance(x, Mapping):
        return {str(k): _canon(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (set, frozenset)):
        return sorted(_canon(v) for v in x)
    if isinstance(x, (list, tuple)):
        return [_canon(v) for v in x]
    if isinstance(x, (int, float, str, bool)) or x is None:
        return x
    raise PartRefused(f"a part's parameter is plain data (numbers, text, lists, maps), not {type(x).__name__}")


def part_sha(part: Mapping[str, Any]) -> str:
    """A part's binding: its factory id, its canonical parameters (and a gate's keys), and its code closure."""
    pid = str(part["id"])
    mod = pid.partition(":")[0]
    return _digest({"id": pid, "params": _canon(part.get("params", {})), "keys": _canon(part.get("keys", [])),
                    "code": code_closure(mod)})


def engine_sha(E: Engine) -> str:
    return _digest({m.__name__: code_closure(m.__name__) for m in E.modules().values()})


def w42_code_sha() -> str:
    return _digest(code_closure("extended.wave42"))


def build_part(part: Mapping[str, Any], *, fixture: bool) -> Any:
    """The part its factory builds from its declared parameters (F-2): `module:function(**params)`."""
    pid = str(part["id"])
    mod, _, attr = pid.partition(":")
    if not attr:
        raise PartRefused(f"a part's id is module:function, got {pid!r}")
    if not fixture and not mod.startswith("extended."):
        raise PartRefused(f"under a pin a part is this repository's own (extended.), not {mod!r}")
    factory = getattr(importlib.import_module(mod), attr)
    return factory(**dict(part.get("params", {})))


def check_bindings(spec: "Spec", E: Engine) -> dict[str, Any]:
    """Every binding recomputed and compared with the declaration's: the parts, the engine and the objective's code."""
    got = {k: part_sha(spec.parts[k]) for k in PART_NAMES}
    got["engine"] = engine_sha(E)
    got["objective_code"] = w42_code_sha()
    want = {k: spec.parts[k]["sha256"] for k in PART_NAMES}
    want["engine"] = spec.parts["engine"]["sha256"]
    want["objective_code"] = spec.raw["objective"]["code_sha256"]
    off = [k for k in got if got[k] != want[k]]
    if off:
        raise PartRefused(f"REFUSED: the binding(s) {off} differ from the declaration's (F-2): "
                          + "; ".join(f"{k} declared {want[k][:12]}, here {got[k][:12]}" for k in off))
    return got


def searched_levers() -> frozenset[str]:
    """The allowlist (F-8): the searched lever ids of the lever table; the side is a declared rule, never one."""
    from extended import lever_space as LS
    return frozenset(k for k, v in LS.LEVERS.items() if v.cls == LS.SEARCHED)


def check_levers(space: Any) -> None:
    allowed = searched_levers()
    bad = [d.name for d in space.dims if str(getattr(d, "lever", "")) not in allowed]
    if bad:
        raise PartRefused(f"REFUSED: the dimension(s) {bad} are not searched levers of the lever table (an allowlist: "
                          "the side is the trigger's, O-4)")


def _space_canon(x: Any) -> Any:
    if callable(x):
        return f"{getattr(x, '__module__', '')}:{getattr(x, '__qualname__', type(x).__name__)}"
    if is_dataclass(x) and not isinstance(x, type):
        return {f.name: _space_canon(getattr(x, f.name)) for f in fields(x)}
    if isinstance(x, Mapping):
        return {str(k): _space_canon(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (set, frozenset)):
        return sorted(str(_space_canon(v)) for v in x)
    if isinstance(x, (list, tuple)):
        return [_space_canon(v) for v in x]
    return x if isinstance(x, (int, float, str, bool)) or x is None else str(x)


def space_digest(space: Any) -> str:
    """The built space's canonical digest, recorded beside the binding (sets sorted: no hash-seed dependence)."""
    return _digest(_space_canon(space))


# ------------------------------------------------------------------------------------------------ the objective


@dataclass(frozen=True)
class Objective:
    """W42-R1's pinned values as the survey reads them (the module docstring)."""

    values: Mapping[str, Any]
    dims: tuple[tuple[Any, float, float, float], ...]          # (wave42.Dim, lo, hi, weight)
    budget: float
    delta: float
    limits: tuple[Mapping[str, Any], ...]                      # name, key, direction <= / >=, horizon, stat, bound
    check_level: float
    no_harm_margin: float
    do_nothing: float                                          # the composite of the design that buys nothing (V-4)


def _wave42() -> Any:
    from extended import wave42
    return wave42


def load_objective(raw: Mapping[str, Any], *, fixture: bool) -> Objective:
    """W42-R1's result file, by its sha256 (F-1, F-11)."""
    W = _wave42()
    p = Path(raw["file"])
    if not p.is_absolute():
        p = ROOT / p
    if not fixture and not _inside(p, ROOT):
        raise SpecRefused(f"REFUSED: under a pin W42-R1's result is this repository's file, not {p}")
    if not p.is_file() or _lf_sha(p) != raw["sha256"]:
        raise SpecRefused(f"REFUSED: W42-R1's result file {p} is missing or does not hash to its declared sha256")
    v = json.loads(p.read_text(encoding="utf-8"))
    if raw["rule_id"] != W42_RULE or v.get("rule_id") != W42_RULE or W.RULE_ID != W42_RULE:
        raise SpecRefused(f"REFUSED: the objective is {W42_RULE}'s, got {raw['rule_id']!r} / {v.get('rule_id')!r}")
    try:
        by = {d.name: d for d in W.DIMENSIONS}
        dims = tuple((by[d["name"]], float(d["lo"]), float(d["hi"]), float(v["weights"][d["name"]]))
                     for d in v["dimensions"] if d["name"] in v["weights"])
        lim_by = {lim.name: lim for lim in W.LIMITS}
        lims = tuple({"name": x["name"], "key": x["key"], "direction": "<=" if x["direction"] == "ceiling" else ">=",
                      "horizon": int(lim_by[x["name"]].horizon), "stat": lim_by[x["name"]].stat,
                      "bound": float(x["value"])} for x in v["limits"]["values"] if x.get("status") == "set")
        ob = Objective(v, dims, float(v["budgets"]["primary"]), float(v["delta_star"]["value"]), lims,
                       float(v["limits"]["check_level"]), float(v["no_harm"]["margin"]),
                       float(v["do_nothing"]["composite"]))
    except (KeyError, TypeError, ValueError) as e:
        raise SpecRefused(f"REFUSED: W42-R1's result lacks {e} (dimensions, weights, budgets, delta*, limits, the "
                          "no-harm margin, the do-nothing composite)") from e
    if not dims or abs(sum(w for *_, w in dims) - 1.0) > 1e-9 or not ob.delta > 0 or not ob.no_harm_margin >= 0:
        raise SpecRefused("REFUSED: W42-R1's weights sum to one, delta* is above zero, the no-harm margin is not "
                          "negative")
    return ob


def composite(ctx: "Context", arm: Mapping[str, Any], sl: Sequence[int]) -> np.ndarray:
    """W42-R1's composite per seed (higher better): C(c) = sum_d w_d mean_{s in E_d} z_d(s, c), by wave42's own
    `_derived`, `_rows` and `_z`, each dimension over its own complete starts."""
    W, ob = ctx.W, ctx.obj
    per = dict(arm)
    per.update(W._derived({k: np.asarray(x, float) for k, x in arm.items()}, ob.budget))
    sl = np.asarray(sl)
    c: Any = 0.0
    for dim, lo, hi, w in ob.dims:
        rows = W._rows(sl, dim.horizon)
        if not rows.any():
            raise SurveyRefused(f"no start is complete over {dim.name}'s horizon {dim.horizon}")
        c = c + w * W._z(dim, np.asarray(per[dim.key], float)[rows], lo, hi).mean(axis=0)
    return np.asarray(c, float)


def limit_value(ctx: "Context", arm: Mapping[str, Any], sl: Sequence[int], lim: Mapping[str, Any]
                ) -> tuple[float, np.ndarray]:
    """A limit's point estimate -- its declared statistic over its complete starts, pooled over seeds (wave42's
    `_stat`) -- and the same statistic seed by seed."""
    W = ctx.W
    per = dict(arm)
    per.update(W._derived({k: np.asarray(x, float) for k, x in arm.items()}, ctx.obj.budget))
    rows = W._rows(np.asarray(sl), lim["horizon"])
    if not rows.any():
        raise SurveyRefused(f"no start is complete over {lim['name']}'s horizon {lim['horizon']}")
    x = np.asarray(per[lim["key"]], float)[rows]
    return W._stat(x, lim["stat"]), np.array([W._stat(x[:, c], lim["stat"]) for c in range(x.shape[1])])


def t_threshold(z: float, n: int) -> float:
    """The declared z read as its one-sided level, then the t quantile at n - 1 degrees of freedom (F-7)."""
    from scipy import stats
    return float(stats.t.ppf(stats.norm.cdf(z), n - 1))


def crossing_check(over: float, se: float, level: float, n: int) -> tuple[float, bool]:
    """The one-sided check of crossing beside a limit (E-230), never deciding: (t, shown at `level`, t law)."""
    from scipy import stats
    t = over / se if se > 0 else (math.inf if over > 0 else -math.inf)
    return t, bool(t > float(stats.t.ppf(1.0 - level, n - 1)))


# ------------------------------------------------------------------------------------------------ the declaration


def _int(x: Any, what: str) -> int:
    if not isinstance(x, int) or isinstance(x, bool):
        raise SpecRefused(f"{what} is an explicit integer, got {x!r}")
    return int(x)


def _ints(xs: Any, what: str) -> tuple[int, ...]:
    if not isinstance(xs, list) or not xs:
        raise SpecRefused(f"{what} is a list of integers")
    return tuple(_int(x, what) for x in xs)


@dataclass(frozen=True)
class Spec:
    """The declaration's survey-spec block, checked."""

    raw: Mapping[str, Any]
    prereg_id: str
    survey_n: int
    method: str
    survey_seed: int
    max_proposals: int
    rounds: int
    round_seed: int
    round_kw: Mapping[str, Any]
    measure: str
    blocks: tuple[tuple[str, str], ...]
    seeds: tuple[int, ...]
    horizon: int
    baselines: tuple[str, ...]
    baseline_seed: int
    candidates: int
    reread_seeds: tuple[int, ...]
    z: float
    plateau_rule: Mapping[str, Any]
    plateau_seed: int
    plateau_box_seed: int | None
    parts: Mapping[str, Any]


def _block(raw: bytes) -> dict[str, Any]:
    found = SPEC_FENCE.findall(raw.replace(b"\r\n", b"\n"))
    if len(found) != 1:
        raise SpecRefused(f"a search declaration carries exactly one ```survey-spec block, found {len(found)}")
    try:
        out = json.loads(found[0].decode("utf-8"))
    except ValueError as e:
        raise SpecRefused(f"the survey-spec block is not JSON (a template placeholder left in?): {e}") from e
    if not isinstance(out, dict):
        raise SpecRefused("the survey-spec block is a JSON object")
    return out


def load_spec(raw: bytes | str) -> Spec:
    """The one survey-spec block of a declaration's bytes (the module docstring), or `SpecRefused`."""
    s = _block(raw.encode("utf-8") if isinstance(raw, str) else raw)
    if set(s) != set(SPEC_KEYS):
        raise SpecRefused(f"the survey-spec keys are exactly {sorted(SPEC_KEYS)}, got {sorted(s)}")
    for k, want in SPEC_KEYS.items():
        if want is not None and (not isinstance(s[k], dict) or set(s[k]) != set(want)):
            got = sorted(s[k]) if isinstance(s[k], dict) else type(s[k]).__name__
            raise SpecRefused(f"survey-spec {k} holds exactly {sorted(want)}, got {got}")
    pid = s["prereg_id"]
    if not isinstance(pid, str) or not re.fullmatch(r"F-\d+", pid):
        raise SpecRefused(f"a search is declared as a family F-NN, got {pid!r}")
    sv, rd, pr, bl, fi, pl, parts = (s[k] for k in ("survey", "rounds", "protocol", "baselines", "finalists",
                                                    "plateau", "parts"))
    if not isinstance(bl["names"], list) or tuple(bl["names"]) != BASELINES:
        raise SpecRefused(f"the baselines are exactly {BASELINES} (CHARTER 3.8 (b)), got {bl['names']!r}")
    seeds, reread = _ints(pr["seeds"], "a protocol seed"), _ints(fi["reread_seeds"], "a re-read seed")
    if len(reread) < MIN_REREAD_SEEDS or len(set(reread)) != len(reread):
        raise SpecRefused(f"at least {MIN_REREAD_SEEDS} distinct re-read seeds, got {len(reread)}")
    if set(seeds) & set(reread):
        raise SpecRefused("the re-read seeds are fresh: disjoint from the selection seeds")
    z = fi["z"]
    if isinstance(z, bool) or not isinstance(z, (int, float)) or not (math.isfinite(z) and z > 0):
        raise SpecRefused(f"the finalists' z is a finite number above zero, got {z!r}")
    rule = pl["rule"]
    if not isinstance(rule, dict) or rule.get("margin") != DELTA_STAR or rule.get("side") != "worse":
        raise SpecRefused("the plateau rule's margin is the word 'delta_star' (W42-R1's, never typed) and its side "
                          "'worse' (n-c)")
    for k in PART_NAMES:
        b = parts[k]
        keys = {"id", "params", "sha256"} | ({"keys"} if k == "gate" else set())
        if not isinstance(b, dict) or set(b) != keys or not isinstance(b["params"], dict) or \
                not re.fullmatch(r"[0-9a-f]{64}", str(b["sha256"])):
            raise SpecRefused(f"the part {k} is {{{', '.join(sorted(keys))}}}, got {b!r}")
    if not isinstance(parts["gate"]["keys"], list) or not parts["gate"]["keys"]:
        raise SpecRefused("the gate declares the keys it reads (F-10)")
    if not isinstance(parts["engine"], dict) or set(parts["engine"]) != {"id", "sha256"}:
        raise SpecRefused("the engine is bound by {id, sha256}")
    ob = s["objective"]
    if not all(isinstance(ob[k], str) for k in ob) or not re.fullmatch(r"[0-9a-f]{64}", ob["sha256"]):
        raise SpecRefused("the objective names W42-R1's rule id, its result file, its sha256 and its code's sha256")
    out = Spec(raw=s, prereg_id=pid, survey_n=_int(sv["n"], "the survey size"), method=str(sv["method"]),
               survey_seed=_int(sv["seed"], "the survey seed"),
               max_proposals=_int(sv["max_proposals"], "max_proposals"),
               rounds=_int(rd["count"], "the rounds' count"), round_seed=_int(rd["seed"], "the rounds' seed"),
               round_kw={k: rd[k] for k in ROUND_KEYS}, measure=str(pr["measure"]),
               blocks=tuple((str(b[0]), str(b[1])) for b in pr["blocks"]), seeds=seeds,
               horizon=_int(pr["horizon"], "the horizon"), baselines=BASELINES,
               baseline_seed=_int(bl["seed"], "the baselines' seed"),
               candidates=_int(fi["candidates"], "the candidates' count"), reread_seeds=reread, z=float(z),
               plateau_rule=dict(rule), plateau_seed=_int(pl["seed"], "the plateau seed"),
               plateau_box_seed=None if pl["box_seed"] is None else _int(pl["box_seed"], "the box seed"),
               parts=dict(parts))
    if out.rounds < 0 or out.candidates < 1 or out.survey_n < 1:
        raise SpecRefused("the rounds a count, the survey and the candidates at least one")
    return out


def fixture_pin(path: Path | str) -> str:
    """A test's stand-in for a pin: honoured only outside `prereg/` and outside any `results/` folder."""
    return FIXTURE_PREFIX + _lf_sha(path)


def _inside(p: Path, d: Path) -> bool:
    try:
        Path(p).resolve().relative_to(Path(d).resolve())
        return True
    except ValueError:
        return False


def _decisions() -> str:
    dec = ROOT / "DECISIONS.md"
    return dec.read_text(encoding="utf-8") if dec.is_file() else ""


def check_pinned(path: Path, sha: str, spec: Spec, *, results_dir: Path, pin_fixture: str | None) -> str:
    """The pin's decision row ("fixture" under a fixture pin), else `NotPinned`; this repository's log only (m-5)."""
    if pin_fixture is not None:
        if _inside(path, ROOT / "prereg"):
            raise NotPinned("REFUSED: a fixture pin never stands for a declaration under prereg/ (pin it by its row)")
        if "results" in {x.lower() for x in results_dir.resolve().parts}:
            raise NotPinned("REFUSED: a fixture-pinned survey writes outside any results/ folder")
        if pin_fixture != FIXTURE_PREFIX + sha:
            raise NotPinned(f"REFUSED: the fixture pin does not match the declaration's LF sha256 {sha[:12]}")
        return "fixture"
    try:
        rel = path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as e:
        raise NotPinned(f"REFUSED: {path} is not a file of this repository ({ROOT})") from e
    if not SEARCH_DECLARATION.fullmatch(rel) or not rel.startswith(f"prereg/{spec.prereg_id}_"):
        raise NotPinned(f"REFUSED: a search's declaration is prereg/{spec.prereg_id}_<name>.md, not {rel}")
    if not _inside(results_dir, ROOT):
        raise NotPinned(f"REFUSED: a pinned survey writes inside this repository's tree, not {results_dir}")
    text = _decisions()
    pinned = R.pins(text).get(rel)
    if not pinned:
        raise NotPinned(f"REFUSED: {rel} is not pinned: no decision row carries its sha256")
    if pinned != {sha}:
        raise NotPinned(f"REFUSED: {rel} hashes to {sha[:12]}, its pin is {sorted(h[:12] for h in pinned)}: a change "
                        "is a new declaration")
    for line in text.splitlines():
        m = R.ROW.match(line)
        if m and f"`{rel}` sha256 `{sha}`" in line:
            return m.group(1)
    raise NotPinned(f"REFUSED: {rel}'s pin is in no decision row")


def check_once(sha: str, results_dir: Path, name: str) -> None:
    """F-5: no output of this run's names in the folder, no variants row of this declaration, no finalists' token for
    it in the decision log."""
    there = [f"{name}_{o}.csv" for o in OUTPUTS if (results_dir / f"{name}_{o}.csv").exists()]
    if there:
        raise RunRepeated(f"REFUSED: {there} exist in {results_dir}: a result is never overwritten")
    if any(r.get("params", {}).get("_declaration_sha256") == sha for r in _existing_rows(results_dir / "variants.jsonl")):
        raise RunRepeated(f"REFUSED: the variants ledger in {results_dir} already counts a run of this declaration "
                          f"({sha[:12]}): a survey is run once")
    if any(t.get("sha") == sha for t in R.heldout_tokens(_decisions(), "finalists")):
        raise RunRepeated(f"REFUSED: a finalists' token for this declaration ({sha[:12]}) is already in the log")


# ------------------------------------------------------------------------------------------------ the context


@dataclass
class Context:
    spec: Spec
    E: Engine
    W: Any
    obj: Objective
    space: Any
    gate: Callable[[Mapping[str, Any]], str | None]
    gate_keys: tuple[str, ...]
    build_schedule: Callable[[Mapping[str, Any]], Any]
    runner: Callable[[Any, Any], RunOutput]
    playbook: Callable[[Mapping[str, Any]], str]
    ledger: Any
    protocol: Any
    limits: tuple[Any, ...]
    sha: str
    writer: Callable[..., Any] | None = None
    variants_writer: Callable[..., Path] | None = None
    rows: list[dict[str, Any]] = field(default_factory=list)
    readings: list[Any] = field(default_factory=list)
    limit_readings: dict[str, list[Any]] = field(default_factory=dict)
    selection: dict[str, dict[str, Any]] = field(default_factory=dict)
    rounds: list[Any] = field(default_factory=list)
    records: list[dict[str, Any]] = field(default_factory=list)
    floored: list[dict[str, Any]] = field(default_factory=list)
    memo: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = field(default_factory=dict)

    @property
    def limit_names(self) -> tuple[str, ...]:
        return tuple(lim["name"] for lim in self.obj.limits)


def new_ledger(E: Engine) -> Any:
    """The run's one cell ledger: the engine's own, whose survey role declares the protocol."""
    return E.SS.CellLedger()


def protocol_digest(p: Any) -> str:
    return _digest({"measure": p.measure, "blocks": [list(b) for b in p.blocks], "seeds": list(p.seeds),
                    "horizon": p.horizon, "libs": [list(x) for x in p.libs]})


def _held_out_first(ctx: Context, out: RunOutput) -> None:
    """F-4: a held-out tag, block or horizon refuses the whole run, before anything else is read of it."""
    SS = ctx.E.SS
    tag = str(out.tag)
    low = tag.lower().replace("-", "").replace("_", "").replace(" ", "")
    if any(w in low for w in _HELD_OUT_WORDS) or tag != SEARCH_TAG:
        raise SS.HeldOutInput(f"REFUSED: the runner labels a run {tag!r}: a search reads the search years only "
                              "(CHARTER 3.6 (a); E-208, E-221 O-1)")
    for b in out.blocks:
        try:
            got = R.blocks_of(b[0], b[1])
        except (R.ReadRefused, ValueError, TypeError) as e:
            raise SS.HeldOutInput(f"REFUSED: the runner reports block {b!r}: {e}") from e
        if got != ("choice",):
            raise SS.HeldOutInput(f"REFUSED: the runner reports block {b!r}, touching the held-out years ({got})")
    SS._check_through(tuple(tuple(b) for b in out.blocks), out.horizon)


def _check_real_path(out: RunOutput, keys: set[str]) -> None:
    if set(out.real_path) != {AS_TRADED, REFLECTED} or any(not keys <= set(v) for v in out.real_path.values()):
        raise SurveyRefused(f"the runner reports exactly the real path's {AS_TRADED} and {REFLECTED} readings, each on "
                            f"every key the composite reads; got {sorted(out.real_path)}")


def _check_output(ctx: Context, out: Any, protocol: Any) -> None:
    """The run's report: held-out first (F-4); then on the protocol given, every arm and key, paired on the same
    starts, one column a seed, each start's sessions left, positions per path."""
    if type(out) is not RunOutput:
        raise SurveyRefused(f"the runner reports a RunOutput, got {type(out).__name__}")
    _held_out_first(ctx, out)
    if tuple(out.seeds) != tuple(protocol.seeds) or tuple(tuple(b) for b in out.blocks) != tuple(protocol.blocks) \
            or out.horizon != protocol.horizon:
        raise SurveyRefused("the runner ran off the protocol it was given (seeds, blocks or horizon)")
    need = set(ctx.W.REQUIRED) | {lim["key"] for lim in ctx.obj.limits if lim["key"] in ctx.W.OPTIONAL}
    missing = [a for a in (DESIGN_ARM,) + ctx.spec.baselines if a not in out.arms or
               not need <= set(out.arms[a])]
    if missing or not set(ctx.gate_keys) <= set(out.arms.get(DESIGN_ARM, {})):
        raise SurveyRefused(f"the runner reports the design's and every baseline's arm on every key W42-R1 reads "
                            f"and the gate's keys; incomplete: {missing or 'the gate keys'}")
    _check_real_path(out, need)
    n = len(out.sessions_left)
    shapes = {np.asarray(x).shape for arm in list(out.arms.values()) + list(out.real_path.values())
              for x in arm.values()}
    if n < 1 or shapes != {(n, len(protocol.seeds))}:
        raise SurveyRefused(f"every arm on the same {n} starts and one column a seed (paired), got {sorted(shapes)}")
    if not isinstance(out.positions, Mapping):
        raise SurveyRefused("the positions are reported per (start, seed) path (n-a)")


def book_check(out: RunOutput) -> None:
    """One user's book per (start, seed) path (`components.UserBook`): opposite positions at once across the user's
    accounts or firms are conduct tier 1, two at once an undefined overlap: `_Refused` either way."""
    from extended import components as C

    for path, ps in sorted(out.positions.items()):
        try:
            C.UserBook().extend(ps)
        except C.TierOneRefused as e:
            raise _Refused("tier1", f"path {path}: {e}") from e
        except C.OverlapRefused as e:
            raise _Refused("overlap", f"path {path}: {e}") from e


def gate_check(ctx: Context, out: RunOutput) -> None:
    """The declared gate on only its declared keys of the design's arm (F-10)."""
    view = MappingProxyType({k: np.asarray(out.arms[DESIGN_ARM][k]) for k in ctx.gate_keys})
    why = ctx.gate(view)
    if why:
        raise _Refused("gate", str(why))


def screen(ctx: Context, out: RunOutput) -> None:
    """Before any measure is read: the user's book (conduct tier 1), then the gate."""
    book_check(out)
    gate_check(ctx, out)


def _reading(ctx: Context, design: Mapping[str, Any], per: Any, value: float | None, out: RunOutput, measure: str,
             reread: bool, roles: Callable[[str], bool]) -> Any:
    SS = ctx.E.SS
    per = np.asarray(per, float).ravel()
    se = float(per.std(ddof=1) / math.sqrt(len(per))) if len(per) > 1 else 0.0
    r = SS.Reading(dict(design), float(per.mean()) if value is None else float(value), tuple(out.blocks),
                   tuple(out.seeds), str(out.tag), measure, out.horizon, se, tuple(per))
    return SS.admit_one(r, ledger=ctx.ledger, measure=measure, reread=reread, roles=roles)


def _row(ctx: Context, role: str, design: Mapping[str, Any], measure: str, r: Any, refused: str = "") -> None:
    ctx.rows.append({"role": role, "id": ctx.E.SS.design_id(design), "measure": measure,
                     "value": None if r is None else float(r.value), "se": None if r is None else float(r.se),
                     "per_seed": "" if r is None else json.dumps(list(r.per_seed)), "refused": refused,
                     "design": json.dumps(dict(design), sort_keys=True, default=str)})


def _roles(ctx: Context, role: str) -> Callable[[str], bool]:
    if role == "plateau":
        return lambda r: r.startswith("plateau:")
    return ctx.E.SS.searched


def _rows_of(ctx: Context, role: str, design: Mapping[str, Any], got: Mapping[str, Any]) -> None:
    for k, r in got.items():
        if k == BASELINE_ROLE:
            for b, rb in r.items():
                _row(ctx, f"{role}:{BASELINE_ROLE}", {"baseline": b}, ctx.spec.measure, rb)
        elif k != "out":
            _row(ctx, role, design, k, r)


def read_design(ctx: Context, design: Mapping[str, Any], protocol: Any, role: str) -> dict[str, Any]:
    """Steps 3-5 (the module docstring): {measure: Reading} for the design and each limit, `BASELINE_ROLE`:
    {baseline: Reading}, `"out"`: the run; `_Refused` when the book or the gate refuses."""
    reread = tuple(protocol.seeds) != tuple(ctx.protocol.seeds)
    key = (ctx.E.SS.design_id(design), tuple(protocol.seeds))
    if key in ctx.memo:
        got = ctx.memo[key]
        _rows_of(ctx, f"{role}(memo)", design, got)                        # n-d: every read reported
        return got
    out = ctx.runner(ctx.build_schedule(dict(design)), protocol)
    _check_output(ctx, out, protocol)
    try:
        screen(ctx, out)
    except _Refused as g:
        _row(ctx, role, design, "", None, f"{g.cls}: {g.reason}")
        raise
    m, sl, roles = ctx.spec.measure, out.sessions_left, _roles(ctx, role)
    got: dict[str, Any] = {m: _reading(ctx, design, -composite(ctx, out.arms[DESIGN_ARM], sl), None, out, m, reread,
                                       roles)}
    for lim in ctx.obj.limits:                                  # every read: a neighbour may later be a candidate
        v, per = limit_value(ctx, out.arms[DESIGN_ARM], sl, lim)
        got[lim["name"]] = _reading(ctx, design, per, v, out, lim["name"], reread, roles)
    got[BASELINE_ROLE] = {b: _reading(ctx, {"baseline": b}, -composite(ctx, out.arms[b], sl), None, out, m, reread,
                                      lambda r: r == BASELINE_ROLE) for b in ctx.spec.baselines}
    got["out"] = out
    _rows_of(ctx, role, design, got)
    ctx.memo[key] = got
    return got


def _keep(ctx: Context, got: Mapping[str, Any]) -> None:
    r = got[ctx.spec.measure]
    ctx.readings.append(r)
    ctx.selection.setdefault(r.id, dict(got))
    for name in ctx.limit_names:
        ctx.limit_readings.setdefault(name, []).append(got[name])


def read_all(ctx: Context, designs: Sequence[Mapping[str, Any]], role: str) -> None:
    for d in designs:
        try:
            _keep(ctx, read_design(ctx, d, ctx.protocol, role))
        except _Refused:
            continue


def draw_survey(ctx: Context) -> list[dict[str, Any]]:
    """Step 2: the space-filling survey, every cell counted under ``survey``, which declares the protocol, the re-read
    seeds and the limit measures to the ledger."""
    s = ctx.spec
    return ctx.E.SS.Sampler(ctx.space, seed=s.survey_seed, method=s.method).survey(
        s.survey_n, ledger=ctx.ledger, protocol=ctx.protocol, reread_seeds=s.reread_seeds,
        measures=ctx.limit_names, max_proposals=s.max_proposals)


def check_engine_rereads(ctx: Context) -> None:
    """Q-192: the engine reads the declared limit measures on the re-read seeds (F-3), or the run refuses here, after
    the survey's cells and before any read."""
    for name in ctx.limit_names:
        try:
            ctx.ledger.protocol_for(name, reread=True)
        except ctx.E.SS.OffProtocol as e:
            raise PartRefused(f"REFUSED: the engine does not read the limit {name!r} on the re-read seeds (Q-192's "
                              f"change; F-3): {e}") from e


def run_rounds(ctx: Context) -> None:
    """Step 6: exactly the declared rounds, each proposed from the surrogate and read."""
    P = ctx.E.P
    spec = P.RoundSpec(**ctx.spec.round_kw)
    for i in range(1, ctx.spec.rounds + 1):
        rnd = P.propose(ctx.space, ctx.readings, spec=spec, round_index=i, seed=ctx.spec.round_seed,
                        ledger=ctx.ledger, limits=ctx.limits,
                        limit_readings=dict(ctx.limit_readings) if ctx.limits else None)
        ctx.rounds.append(rnd)
        read_all(ctx, rnd.designs, f"round-{i}")


NOT_PAID = "not_paid_within_B"


def do_nothing_floor(ctx: Context, r: Any) -> tuple[bool, dict[str, Any]]:
    """V-4: the composite (the reading's minimised value, negated) strictly above the do-nothing design's, on the point
    estimate: a design that buys nothing scores W42-R1's `do_nothing` composite and is never a finalist."""
    c = -float(r.value)
    return c > ctx.obj.do_nothing, {"do_nothing": {"composite": c, "do_nothing": ctx.obj.do_nothing,
                                                   "held": bool(c > ctx.obj.do_nothing)}}


def not_paid_floor(ctx: Context, got: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    """V-4: the `not_paid_within_B` limit's point estimate inside its bound (when W42-R1 sets it)."""
    lim = next((x for x in ctx.obj.limits if x["name"] == NOT_PAID), None)
    if lim is None:
        return True, {"not_paid": {"set": False}}
    v = float(got[NOT_PAID].value)
    ok = v <= lim["bound"] if lim["direction"] == "<=" else v >= lim["bound"]
    return ok, {"not_paid": {"set": True, "value": v, "bound": lim["bound"], "held": bool(ok)}}


def passes_floors(ctx: Context, got: Mapping[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    """V-4's floors, in their order -- the no-harm floor, the `not_paid_within_B` limit, the do-nothing floor: (passes,
    the first floor failed, every floor's reading)."""
    info: dict[str, Any] = {}
    first = ""
    for name, (ok, part) in (("the no-harm floor", no_harm(ctx, got["out"])),
                             ("the not_paid_within_B limit", not_paid_floor(ctx, got)),
                             ("the do-nothing floor", do_nothing_floor(ctx, got[ctx.spec.measure]))):
        info.update(part)
        if not ok and not first:
            first = name
    return not first, first, info


def finalist_candidates(ctx: Context) -> list[Any]:
    """The finalist order rule: **the floors first** (V-4: `passes_floors` on each cell's selection run; a cell that
    fails one is recorded, never ranked), then the cells left by selection reading, lowest first (ties by id), the
    first `candidates`."""
    seen: dict[str, Any] = {}
    for r in ctx.readings:
        seen.setdefault(r.id, r)
    kept = []
    for r in sorted(seen.values(), key=lambda r: (float(r.value), r.id)):
        ok, first, info = passes_floors(ctx, ctx.selection[r.id])
        if ok:
            kept.append(r)
        else:
            ctx.floored.append({"id": r.id, "selection_value": float(r.value), "design": dict(r.design),
                                "reason": f"before ranking, fails {first}", **info})
    return kept[:ctx.spec.candidates]


def beats_baselines(ctx: Context, got: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    """On the re-read: each baseline's paired gap (baseline - candidate, minimised units) past delta* on the t law."""
    mine = np.asarray(got[ctx.spec.measure].per_seed, float)
    thr = t_threshold(ctx.spec.z, len(mine))
    gaps, ok = {}, True
    for b in ctx.spec.baselines:
        diff = np.asarray(got[BASELINE_ROLE][b].per_seed, float) - mine
        d = float(diff.mean())
        se = float(diff.std(ddof=1) / math.sqrt(len(diff)))
        t = (d - ctx.obj.delta) / se if se > 0 else (math.inf if d > ctx.obj.delta else -math.inf)
        gaps[b] = {"gap": d, "se": se, "t": t, "threshold": thr, "beaten": bool(t > thr)}
        ok = ok and gaps[b]["beaten"]
    return ok, {"gaps": gaps}


def limits_inside(ctx: Context, reread: Mapping[str, Any], selection: Mapping[str, Any]) -> tuple[bool, dict]:
    """F-3, E-230: each limit's **re-read** point estimate inside its bound decides; the selection reading and the
    one-sided check of crossing (t law, W42-R1's level) beside, never deciding."""
    out, ok = {}, True
    for lim in ctx.obj.limits:
        r, s = reread[lim["name"]], selection.get(lim["name"])
        v, b = float(r.value), float(lim["bound"])
        inside = v <= b if lim["direction"] == "<=" else v >= b
        over = (v - b) if lim["direction"] == "<=" else (b - v)
        t, shown = crossing_check(over, float(r.se or 0.0), ctx.obj.check_level, len(r.per_seed))
        out[lim["name"]] = {"value": v, "bound": b, "direction": lim["direction"], "stat": lim["stat"],
                            "inside": inside, "selection_value": None if s is None else float(s.value),
                            "check_t": t, "check_level": ctx.obj.check_level, "crossing_shown": shown}
        ok = ok and inside
    return ok, {"limits": out}


def no_harm(ctx: Context, out: RunOutput) -> tuple[bool, dict[str, Any]]:
    """O-4's floor: the trigger's own sides, and the as-traded composite no worse than the coin-side as-walked
    (`REFLECTED`) composite by more than W42-R1's no-harm margin (point estimates, CHARTER 3.8 (c))."""
    d = float(np.mean(composite(ctx, out.real_path[AS_TRADED], out.sessions_left)
                      - composite(ctx, out.real_path[REFLECTED], out.sessions_left)))
    held = out.side_source == TRIGGER and d >= -ctx.obj.no_harm_margin
    return held, {"no_harm": {"side_source": out.side_source, "as_traded_minus_reflected": d,
                              "margin": ctx.obj.no_harm_margin, "held": bool(held)}}


def plateau_step(ctx: Context, finalist: Any) -> Any:
    """`plateau.check` on the ledger's re-read seeds, its margin delta*; a neighbour refused by the book or the gate
    refuses the candidate (raised as `_Refused`)."""
    PL = ctx.E.PL
    rule = PL.PlateauRule(**dict(ctx.spec.plateau_rule, margin=ctx.obj.delta))

    def evaluate(design: Mapping[str, Any], *, protocol: Any) -> Any:
        return read_design(ctx, design, protocol, "plateau")[ctx.spec.measure]

    return PL.check(finalist, ctx.space, rule, evaluate, ledger=ctx.ledger, ledger_seed=ctx.spec.plateau_seed,
                    seed=ctx.spec.plateau_box_seed)


def choose_finalists(ctx: Context) -> list[dict[str, Any]]:
    """Step 7 (the module docstring): the finalists in order; every candidate's record in `ctx.records`."""
    SS = ctx.E.SS
    finalists = []
    for rank, cand in enumerate(finalist_candidates(ctx), 1):
        rec: dict[str, Any] = {"rank": rank, "id": cand.id, "selection_value": float(cand.value),
                               "design": dict(cand.design)}
        ctx.records.append(rec)
        try:
            got = read_design(ctx, cand.design, ctx.ledger.reread, "reread")
        except _Refused as g:
            rec.update(kept=False, reason=f"refused on the re-read ({g.cls}): {g.reason}")
            continue
        rec["reread_value"] = float(got[ctx.spec.measure].value)
        steps = (("beats each baseline", beats_baselines(ctx, got)),
                 ("every limit inside", limits_inside(ctx, got, ctx.selection.get(cand.id, {}))),
                 ("the no-harm floor", no_harm(ctx, got["out"])),
                 ("the do-nothing floor", do_nothing_floor(ctx, got[ctx.spec.measure])))
        for _, (_, info) in steps:
            rec.update(info)
        failed = [name for name, (ok, _) in steps if not ok]
        if failed:
            rec.update(kept=False, reason="fails: " + "; ".join(failed))
            continue
        try:
            v = plateau_step(ctx, SS.admit_one(cand, ledger=ctx.ledger, roles=SS.searched))
        except _Refused as g:
            rec.update(kept=False, reason=f"a plateau neighbour is refused ({g.cls}): {g.reason}")
            continue
        rec.update(plateau={"accepted": bool(v.accepted), "reason": v.reason, "rule": v.rule,
                            "evaluated": v.evaluated, "held": v.held}, kept=bool(v.accepted), reason=v.reason)
        if v.accepted:
            finalists.append(rec)
    return finalists


# ------------------------------------------------------------------------------------------------ the emission


def heldout_problems(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Each variants row naming the held-out years (a date from 2024-01-02 in any value) or a held-out tag in its label
    or prereg id -- tags and dates, never substrings of design keys (n-4)."""
    out = []
    for i, row in enumerate(rows):
        tags = " ".join(str(row.get(k, "")) for k in ("label", "prereg_id"))
        late = [d for d in _ISO.findall(json.dumps(row, sort_keys=True, default=str)) if d >= str(R.JUDGED_START)]
        tag = _HELD_OUT_LABEL.search(tags)
        if tag or late:
            out.append(f"row {i}: names {tag.group(0) if tag else late[0]!r}")
    return out


def _existing_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def vendored_variants_writer(rows: Sequence[Mapping[str, Any]], results_dir: Path) -> Path:
    """Every row through the vendored `VariantCounter` into `results_dir/variants.jsonl`; a `results/` folder of this
    repository only inside a clean run (`extended.results`' rule)."""
    from extended import results as XR                                   # puts the vendored tree on sys.path

    if XR.protected(results_dir):
        bad = XR.clean_run_problem()
        if bad:
            raise XR.CleanRunRequired(f"REFUSED: the variants ledger in {results_dir} is written only by a clean run "
                                      f"-- {bad}")
    from propedge.backtest.harness import VariantCounter

    counter = VariantCounter(path=Path(results_dir) / "variants.jsonl")
    for r in rows:
        counter.record(prereg_id=r["prereg_id"], params=dict(r["params"]), seed=int(r["seed"]), label=r["label"])
    return counter.path


def _writers(ctx: Context) -> tuple[Callable[..., Any], Callable[..., Path]]:
    if ctx.writer is not None:
        w = ctx.writer
    else:
        from extended.results import write_result as w
    return w, (ctx.variants_writer or vendored_variants_writer)


def variant_rows(ctx: Context) -> list[dict[str, Any]]:
    """The ledger's rows, each carrying the declaration's and the protocol's sha256 (rb2-a), checked held-out free."""
    pdg = protocol_digest(ctx.protocol)
    rows = [dict(r, params=dict(r["params"], _declaration_sha256=ctx.sha, _protocol_sha256=pdg))
            for r in ctx.ledger.variant_rows(ctx.spec.prereg_id)]
    bad = heldout_problems(rows)
    if bad:
        raise HeldOutRow(f"REFUSED: a variants row names the held-out years: {bad[:3]}")
    return rows


def _common(ctx: Context, params: Mapping[str, Any], results_dir: Path) -> dict[str, Any]:
    return dict(script="extended/survey.py", seed=ctx.spec.survey_seed, parameters=dict(params),
                results_dir=results_dir, prereg_id=ctx.spec.prereg_id, variant_count=int(ctx.ledger.counts()["cells"]))


def _records_frame(ctx: Context) -> Any:
    import pandas as pd

    cols = ["rank", "id", "kept", "reason", "selection_value", "reread_value", "design", "detail"]
    rows = [{"rank": r["rank"], "id": r["id"], "kept": bool(r.get("kept", False)), "reason": r.get("reason", ""),
             "selection_value": r["selection_value"], "reread_value": r.get("reread_value"),
             "design": json.dumps(r["design"], sort_keys=True, default=str),
             "detail": json.dumps({k: r[k] for k in ("gaps", "limits", "no_harm", "do_nothing", "plateau") if k in r},
                                  sort_keys=True, default=str)} for r in ctx.records]
    rows += [{"rank": 0, "id": r["id"], "kept": False, "reason": r["reason"], "selection_value": r["selection_value"],
              "reread_value": None, "design": json.dumps(r["design"], sort_keys=True, default=str),
              "detail": json.dumps({k: r[k] for k in ("no_harm", "not_paid", "do_nothing") if k in r},
                                   sort_keys=True, default=str)} for r in ctx.floored]
    return pd.DataFrame(rows, columns=cols)


def emit(ctx: Context, finalists: Sequence[Mapping[str, Any]], *, params: Mapping[str, Any], results_dir: Path,
         name: str) -> dict[str, Any]:
    """Step 8: the readings, the candidates' records and the finalists' list, then the variants (the module
    docstring)."""
    import pandas as pd

    rows = variant_rows(ctx)
    write, vwrite = _writers(ctx)
    fits = [_digest(r.fit) for r in ctx.rounds] + [_digest(f) for r in ctx.rounds for f in r.limit_fits.values()]
    common = _common(ctx, dict(params, fit_sha256=fits, counts=ctx.ledger.counts()), results_dir)
    rd = pd.DataFrame(ctx.rows, columns=["role", "id", "measure", "value", "se", "per_seed", "refused", "design"])
    rpath, _ = write(rd, f"{name}_readings", description=f"{ctx.spec.prereg_id}: every reading of the survey, its "
                     "rounds, the re-reads, the baselines and the plateau checks (search years only)", **common)
    cpath, _ = write(_records_frame(ctx), f"{name}_candidates", description=f"{ctx.spec.prereg_id}: every "
                     "candidate of the finalist order rule, in rank order, kept or refused and why", **common)
    out = []
    for i, f in enumerate(finalists, 1):
        text = str(ctx.playbook(dict(f["design"]))).replace("\r\n", "\n")
        out.append({"order": i, "id": f["id"], "design": json.dumps(f["design"], sort_keys=True, default=str),
                    "selection_value": f["selection_value"], "reread_value": f["reread_value"],
                    "gaps": json.dumps(f["gaps"], sort_keys=True), "limits": json.dumps(f["limits"], sort_keys=True),
                    "no_harm": json.dumps(f["no_harm"], sort_keys=True), "plateau_rule": f["plateau"]["rule"],
                    "plateau_reason": f["plateau"]["reason"], "playbook": text,
                    "playbook_sha256": hashlib.sha256(text.encode()).hexdigest(), "fit_sha256": json.dumps(fits)})
    cols = ["order", "id", "design", "selection_value", "reread_value", "gaps", "limits", "no_harm", "plateau_rule",
            "plateau_reason", "playbook", "playbook_sha256", "fit_sha256"]
    lpath, _ = write(pd.DataFrame(out, columns=cols), f"{name}_finalists",
                     description=f"{ctx.spec.prereg_id}: the finalists' list in the declared order (the finalist "
                     "order rule; empty when none)", **common)
    lsha = _lf_sha(lpath)
    vpath = vwrite(rows, results_dir)                       # last: no counted rows without their results
    token = f"heldout-finalists: {ctx.spec.prereg_id} @ {ctx.sha} list {lsha}" if out else None
    return {"variants": Path(vpath), "readings": Path(rpath), "candidates": Path(cpath), "list": Path(lpath),
            "list_sha256": lsha, "token": token, "fit_sha256": fits}


def emit_failure(ctx: Context, exc: BaseException, *, params: Mapping[str, Any], results_dir: Path,
                 name: str) -> None:
    """m-4, F-6: a refusal after the survey's first cell -- the variants rows, then the failure record, each attempted
    whatever the other does; a failure of either is noted on the refusal."""
    import pandas as pd

    write, vwrite = _writers(ctx)
    try:
        vwrite(variant_rows(ctx), results_dir)
    except Exception as e:
        exc.add_note(f"the variants rows could not be written: {type(e).__name__}: {e}")
    try:
        common = _common(ctx, dict(params, counts=ctx.ledger.counts(), failed=type(exc).__name__), results_dir)
        df = pd.DataFrame([{"exception": type(exc).__name__, "message": str(exc)[:2000],
                            "counts": json.dumps(ctx.ledger.counts(), sort_keys=True),
                            "candidates": _records_frame(ctx).to_json(orient="records")}])
        write(df, f"{name}_failure", description=f"{ctx.spec.prereg_id}: the survey refused after its first cell; "
              "its record and the counts (its variants rows written before it)", **common)
    except Exception as e:
        exc.add_note(f"the failure record could not be written: {type(e).__name__}: {e}")


# ------------------------------------------------------------------------------------------------ the driver


@dataclass
class Outcome:
    declaration_sha256: str
    pin_row: str
    finalists: list[dict[str, Any]]
    candidates: list[dict[str, Any]]
    floored: list[dict[str, Any]]
    token: str | None
    list_path: Path
    list_sha256: str
    readings_path: Path
    candidates_path: Path
    variants_path: Path
    counts: dict[str, Any]
    ledger: Any
    rounds: list[Any]
    bindings: dict[str, Any]


def run_survey(declaration: Path | str, *, results_dir: Path | str, name: str, pin_fixture: str | None = None,
               engine: Engine | None = None, writer: Callable[..., Any] | None = None,
               variants_writer: Callable[..., Path] | None = None) -> Outcome:
    """The whole loop (the module docstring): refusals first, then steps 2-8. `engine` and the writers are honoured
    only under a fixture pin (and the engine is still bound)."""
    path, out_dir = Path(declaration), Path(results_dir)
    if not path.is_file():
        raise NotPinned(f"REFUSED: the declaration {path} does not exist")
    raw = path.read_bytes()                                                # read once: hashed and parsed (n-3)
    sha = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    spec = load_spec(raw)
    pin_row = check_pinned(path, sha, spec, results_dir=out_dir, pin_fixture=pin_fixture)
    fixture = pin_fixture is not None
    if not fixture and any(x is not None for x in (engine, writer, variants_writer)):
        raise PartRefused("REFUSED: under a pin the engine and the writers are this repository's own; an injected "
                          "one is honoured only under a fixture pin")
    commit = "fixture"
    if not fixture:
        dirty = R._dirty(ROOT)
        if dirty:
            raise PartRefused(f"REFUSED: under a pin the tree is clean (its commit binds the code); dirty: {dirty[:5]}")
        commit = R._commit(ROOT, "the survey")
    E = engine or Engine.default()
    E.check()
    bound = check_bindings(spec, E)
    obj = load_objective(spec.raw["objective"], fixture=fixture)
    parts = {k: build_part(spec.parts[k], fixture=fixture) for k in PART_NAMES}
    check_levers(parts["space"])
    protocol = E.SS.Protocol(spec.measure, spec.blocks, spec.seeds, spec.horizon)       # refuses held-out blocks
    bad = heldout_problems(_existing_rows(out_dir / "variants.jsonl"))
    if bad:
        raise HeldOutRow(f"REFUSED: the variants ledger in {out_dir} already holds a held-out row: {bad[:3]}")
    check_once(sha, out_dir, name)
    limits = tuple(E.P.Limit(lim["name"], lim["bound"], lim["direction"]) for lim in obj.limits)
    ctx = Context(spec, E, _wave42(), obj, parts["space"], parts["gate"], tuple(spec.parts["gate"]["keys"]),
                  parts["schedule_builder"], parts["runner"], parts["playbook"], new_ledger(E), protocol, limits, sha,
                  writer, variants_writer)
    params = {"declaration_sha256": sha, "pin_row": pin_row, "commit": commit,
              "protocol_sha256": protocol_digest(protocol), "spec": spec.raw, "bindings": bound,
              "space_digest": space_digest(parts["space"]), "objective_sha256": spec.raw["objective"]["sha256"],
              "round_spec": asdict(E.P.RoundSpec(**spec.round_kw)), "task": TASK}
    try:
        designs = draw_survey(ctx)
        if protocol_digest(ctx.ledger.protocol) != protocol_digest(protocol) or \
                tuple(ctx.ledger.reread.seeds) != spec.reread_seeds:
            raise SurveyRefused("the ledger's protocol is not the pinned declaration's (rb2-a)")
        check_engine_rereads(ctx)
        ctx.ledger.begin(BASELINE_ROLE, spec.baseline_seed)
        for b in spec.baselines:
            ctx.ledger.record(ctx.space, {"baseline": b}, role=BASELINE_ROLE, seed=spec.baseline_seed, refusal=None)
        read_all(ctx, designs, "survey")
        run_rounds(ctx)
        finalists = choose_finalists(ctx)
        em = emit(ctx, finalists, params=params, results_dir=out_dir, name=name)
    except Exception as exc:
        if ctx.ledger.rows:
            emit_failure(ctx, exc, params=params, results_dir=out_dir, name=name)
        raise
    return Outcome(sha, pin_row, finalists, list(ctx.records), list(ctx.floored), em["token"], em["list"], em["list_sha256"],
                   em["readings"], em["candidates"], em["variants"], ctx.ledger.counts(), ctx.ledger, ctx.rounds,
                   bound)


def declare_parts(parts: Mapping[str, Mapping[str, Any]], engine: Engine | None = None) -> dict[str, Any]:
    """The `parts` block of a declaration for these factory ids and parameters, each with its binding (a drafting
    aid: the declaration's author runs it; the red team reads the result)."""
    out = {k: dict(v, sha256=part_sha(v)) for k, v in parts.items()}
    out["engine"] = {"id": f"wave34@{ENGINE_COMMIT}", "sha256": engine_sha(engine or Engine.default())}
    return out


__all__ = ["TASK", "ENGINE_COMMIT", "W42_RULE", "DESIGN_ARM", "BASELINE_ROLE", "BASELINES", "MIN_REREAD_SEEDS",
           "AS_TRADED", "REFLECTED", "TRIGGER", "SEARCH_TAG", "DELTA_STAR", "FIXTURE_PREFIX", "PART_NAMES",
           "SurveyRefused", "NotPinned", "SpecRefused", "PartRefused", "RunRepeated", "HeldOutRow", "RunOutput",
           "Engine", "Objective", "Spec", "Context", "Outcome", "code_closure", "part_sha", "engine_sha",
           "w42_code_sha", "build_part", "check_bindings", "searched_levers", "check_levers", "space_digest",
           "load_objective", "composite", "limit_value", "t_threshold", "crossing_check", "load_spec", "fixture_pin",
           "check_pinned", "check_once", "new_ledger", "protocol_digest", "book_check", "gate_check", "screen",
           "read_design", "read_all", "draw_survey", "check_engine_rereads", "run_rounds", "finalist_candidates",
           "beats_baselines", "limits_inside", "no_harm", "do_nothing_floor", "not_paid_floor",
           "passes_floors", "NOT_PAID", "plateau_step", "choose_finalists", "heldout_problems",
           "vendored_variants_writer", "variant_rows", "emit", "emit_failure", "run_survey", "declare_parts"]
