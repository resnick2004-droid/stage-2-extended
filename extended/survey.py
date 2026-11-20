"""Wave 5 (the restart plan, Waves 5-6; CHARTER 3.3, 3.5, 3.6, 3.8, 3.9; the design-search template's sections 6, 7
and 14): the survey runner -- the end-to-end driver of one declared design search, on the search years only.

    from extended import survey as SV
    parts = SV.Parts(space=space, build_schedule=build, runner=run, gate=gate)
    out = SV.run_survey("prereg/F-NN_<name>.md", parts, results_dir=..., name="F-NN_survey")
    out.token          # "heldout-finalists: F-NN @ <declaration sha> list <list sha>", or None (no finalist)

Built on Wave 3.4's engine as it stood (`wt/wt-features` df367a7; `Engine.check` refuses any other API): **the survey
declares the protocol to the one cell ledger** (`Sampler.survey(..., protocol=, reread_seeds=, measures=)`) and every
door takes it from there (`search_space.admit_one(..., measure=, reread=)`), never from this module's callers.

**Refusals first** (nothing is written by these): the declaration's bytes are read once, hashed (LF sha256) and parsed
from the same bytes (n-3); its one fenced ```` ```survey-spec ```` JSON block holds every number (`load_spec`: every key
required, none unknown, every seed an explicit integer, the baselines exactly `BASELINES`, at least
`MIN_REREAD_SEEDS` fresh re-read seeds, the margin and z strictly positive); the file is **pinned** -- its sha256 in a
pin of exactly its path `prereg/F-NN_<name>.md` in **this repository's** `DECISIONS.md` (`ROOT`; the pin's row
recorded), the results folder inside this tree -- or, for a test, carries `fixture_pin(path)` (honoured only for a file
outside `prereg/`, writing outside any `results/` folder); **every injected part is bound to the declaration**
(`bindings`: the lever space by the digest of its canonical form, the gate, the schedule builder and the runner by
their declared id and their source file's LF sha256 -- plus `survey_config()`'s digest when the part's object has one,
its settings and data files' shas -- and the engine by its four modules' shas), a part that differs from the pin
refused (`PartRefused`), the engine and the writers injectable only under a fixture pin; a searched lever that sets a
side is refused (O-4: the side is the trigger's); the protocol is built from the spec and refuses the held-out years
at construction.

**The loop**, each step a function of this module (so a test can mutate it):
2. `draw_survey`: the space-filling survey; every cell counted under ``survey``; the ledger's protocol then checked
   against the spec's by digest (rb2-a);
3-5. `read_design`: the schedule built from the design, run through the three-way runner (`RunOutput`: per arm -- the
   design's and each baseline's, paired on the same starts -- a start-by-seed matrix per key; the design's real-path
   as-traded and reflected readings; where its sides come from; every position it opens), checked (`_check_output`),
   then **refused before any measure is read** if the user's book refuses its positions (`components.UserBook`: two
   opposite positions across the user's accounts or firms are conduct tier 1) or the declared gate (supply, resolution,
   realised risk) refuses it -- the cell stays counted; else the composite (`composite_score`, built from the spec's
   dimensions, never passed in) and each limit measure scored into a `Reading` and **admitted through the door** at
   once, so a held-out reading refuses at its read;
6. `run_rounds`: exactly the declared rounds (`proposer.propose`), each proposal read; never extended;
7. `choose_finalists`, by **the finalist order rule** declared here: the read survey and round cells by selection
   reading (the minimised composite, ties by id), the first `candidates`; each re-read on the declared fresh seeds
   beside every baseline (paired, the same run) and kept only if (a) it beats **each** baseline by more than the margin
   at the declared z, one-sided and paired over the re-read seeds (`beats_baselines`); (b) every limit's point estimate
   on its selection reading is inside its bound (E-230: the point estimate governs; the one-sided check of crossing at
   the declared level reported beside, never deciding; the engine reads limit measures on the selection seeds only);
   (c) **the no-harm floor** (O-4, `no_harm`): its sides come from its own trigger and its real-path as-traded
   composite is no worse than the reflected (coin) composite by more than the declared margin; (d) `plateau.check`
   accepts it. A plateau neighbour refused by the book or the gate refuses the candidate;
8. `emit`: the readings, every candidate's record, and **the finalists' list**, through `extended.results.write_result`
   by default (a `results/` folder only inside a clean run), **then** the variants ledger (`ledger.variant_rows`, each
   row carrying the declaration's and the protocol's sha256, through the vendored `VariantCounter`; a held-out row
   refused first) -- variants last, so a writer failure leaves no counted rows without their results; the token in
   Q-158's form, `heldout-finalists: F-NN @ <the declaration's LF sha256> list <the list file's LF sha256>`. No finalist:
   the list is written empty and the token is None (the search closes).
**A refusal after the survey's first cell** (any exception) writes a failure record and the ledger's variants rows, in
that order, and is re-raised (m-4): no counted cell vanishes.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import math
import re
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from extended import ROOT
from extended import reader as R

TASK = "Wave 5"
ENGINE_COMMIT = "df367a7"
DESIGN_ARM = "design"
BASELINE_ROLE = "baseline"
BASELINES = ("naive_coin", "p14", "p15", "p16")       # CHARTER 2, 3.8 (b): Topstep's baseline set (E-221)
MIN_REREAD_SEEDS = 5                                    # the lead's floor (Q-186 cycle 1, m-1)
AS_TRADED, REFLECTED = "as_traded", "reflected"
TRIGGER = "trigger"
SPEC_FENCE = re.compile(rb"^```survey-spec[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
FIXTURE_PREFIX = "survey-fixture-pin:"
SEARCH_DECLARATION = re.compile(r"prereg/F-\d+_[^/`]*\.md")
PART_NAMES = ("space", "gate", "schedule_builder", "runner", "engine")
SIDE_WORDS = frozenset({"long", "short", "buy", "sell"})
_SIDE_NAME = re.compile(r"(?:^|[._])side(?:$|[._])", re.IGNORECASE)
_HELD_OUT_LABEL = re.compile(r"held[-_ ]?out|judged|confirmation", re.IGNORECASE)
_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

ROUND_KEYS = ("batch", "pool", "acquisition", "kappa", "xi", "centres", "local", "local_scale", "restarts",
              "p_feasible")
SPEC_KEYS: dict[str, tuple[str, ...] | None] = {
    "prereg_id": None,
    "survey": ("n", "method", "seed", "max_proposals"),
    "rounds": ("count", "seed") + ROUND_KEYS,
    "protocol": ("measure", "blocks", "seeds", "horizon"),
    "composite": ("dims",),
    "limits": ("list", "check_level"),
    "baselines": ("names", "seed"),
    "finalists": ("candidates", "reread_seeds", "margin", "z"),
    "no_harm": ("margin",),
    "plateau": ("rule", "seed", "box_seed"),
    "parts": PART_NAMES,
}


class SurveyRefused(RuntimeError):
    """A survey this module cannot stand behind."""


class NotPinned(SurveyRefused):
    """The declaration is not pinned by a row of this repository's decision log (nor a test's fixture)."""


class SpecRefused(SurveyRefused):
    """The declaration's survey-spec block is missing, malformed, or off its form."""


class PartRefused(SurveyRefused):
    """An injected part that is not the one the declaration binds, or a part the runner never accepts."""


class HeldOutRow(SurveyRefused):
    """A variants row naming the held-out years or a held-out tag (CHARTER 3.3 (f))."""


class _Refused(Exception):
    """A design refused at its read, before any measure (the book or the gate): its cell stays counted."""

    def __init__(self, cls: str, reason: str):
        super().__init__(f"{cls}: {reason}")
        self.cls, self.reason = cls, reason


# ------------------------------------------------------------------------------------------------ the parts


@dataclass(frozen=True)
class RunOutput:
    """What the three-way runner reports for one design on one protocol (the module docstring): `arms[arm][key]` a
    start-by-seed matrix for `DESIGN_ARM` and each baseline, on the same starts; `real_path[AS_TRADED | REFLECTED]
    [key]` the design's real-path readings (the no-harm floor's, never the deciding reading); `side_source` where its
    sides come from (`TRIGGER` for a playbook side); `positions` every `components.Position` it opens, across the
    user's accounts and firms; the seeds, blocks and horizon it ran; its tag."""

    arms: Mapping[str, Mapping[str, Any]]
    real_path: Mapping[str, Mapping[str, Any]]
    side_source: str
    positions: tuple[Any, ...]
    seeds: tuple[int, ...]
    blocks: tuple[tuple[str, str], ...]
    horizon: int
    tag: str = "search"


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
        SS, PL = self.SS, self.PL
        want = [(SS.Sampler.survey, ("protocol", "reread_seeds", "measures")), (SS.admit_one, ("measure", "reread")),
                (SS.CellLedger.begin, ("protocol", "reread_seeds", "measures"))]
        for fn, names in want:
            got = inspect.signature(fn).parameters
            if not all(n in got for n in names):
                raise PartRefused(f"the engine's {fn.__qualname__} lacks {names}: not the engine that stood "
                                  f"({ENGINE_COMMIT})")
        if "protocol" in inspect.signature(PL.check).parameters or not hasattr(SS.CellLedger, "protocol_for") \
                or "reads_through" in {f.name for f in fields(SS.Reading)}:
            raise PartRefused(f"the engine is not the one that stood ({ENGINE_COMMIT}): the doors take a caller's "
                              "protocol")


@dataclass
class Parts:
    """The survey's parts (dependency injection), each bound to the declaration (`bindings`): the lever space;
    `build_schedule(design)`; `runner(schedule, protocol) -> RunOutput`; `gate(RunOutput) -> reason or None` (required:
    supply, resolution, realised risk); and, optional, `playbook(design) -> text`, the engine, the result writer
    (`extended.results.write_result`'s signature) and the variants writer (`(rows, results_dir) -> path`) -- the last
    three honoured only under a fixture pin."""

    space: Any
    build_schedule: Callable[[Mapping[str, Any]], Any]
    runner: Callable[[Any, Any], RunOutput]
    gate: Callable[[RunOutput], str | None]
    playbook: Callable[[Mapping[str, Any]], str] | None = None
    engine: Engine | None = None
    writer: Callable[..., Any] | None = None
    variants_writer: Callable[[Sequence[Mapping[str, Any]], Path], Path] | None = None


def _file_sha(p: Any) -> str:
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _digest(obj: Any) -> str:
    if is_dataclass(obj) and not isinstance(obj, type):
        obj = asdict(obj)
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def part_binding(fn: Any) -> dict[str, str]:
    """A callable's binding: its declared id (module and qualified name), its source file's LF sha256, and, when its
    object has `survey_config()` (its settings, its data files' sha256), that config's digest."""
    if not callable(fn):
        raise PartRefused(f"a part is a callable, got {type(fn).__name__}")
    f = getattr(fn, "__func__", fn)
    src = inspect.getsourcefile(f)
    if src is None:
        raise PartRefused(f"{fn!r} has no source file to bind")
    out = {"id": f"{f.__module__}:{f.__qualname__}", "sha256": _file_sha(src)}
    owner = getattr(fn, "__self__", None)
    if owner is not None and hasattr(owner, "survey_config"):
        out["config"] = _digest(owner.survey_config())
    return out


def _canon(x: Any) -> Any:
    if callable(x):
        return part_binding(x)
    if isinstance(x, Mapping):
        return {str(k): _canon(v) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (list, tuple)):
        return [_canon(v) for v in x]
    if is_dataclass(x) and not isinstance(x, type):
        return {f.name: _canon(getattr(x, f.name)) for f in fields(x)}
    return x if isinstance(x, (int, float, str, bool)) or x is None else str(x)


def space_digest(space: Any) -> str:
    """The lever space's digest: the canonical JSON of every field (dimensions with their bounds, lattices and cells,
    fixed and refused levers, slots, constraints, session anchors, days); a callable by its binding."""
    return _digest(_canon(space))


def engine_binding(E: Engine) -> dict[str, str]:
    return {"id": f"wave34@{ENGINE_COMMIT}",
            "sha256": _digest({k: _file_sha(inspect.getsourcefile(m)) for k, m in sorted(E.modules().items())})}


def bindings(parts: Parts, engine: Engine | None = None) -> dict[str, Any]:
    """Every part's binding, as the declaration's `parts` holds them."""
    E = engine or parts.engine or Engine.default()
    return {"space": {"id": "lever-space", "sha256": space_digest(parts.space)},
            "gate": part_binding(parts.gate), "schedule_builder": part_binding(parts.build_schedule),
            "runner": part_binding(parts.runner), "engine": engine_binding(E)}


def side_levers(space: Any) -> list[str]:
    """The searched levers that set a side (O-4: refused; the side is the trigger's)."""
    out = []
    for d in space.dims:
        cells = tuple(getattr(d, "values", ()) or ()) + tuple(getattr(d, "labels", ()) or ())
        if _SIDE_NAME.search(d.name) or str(getattr(d, "lever", "")).lower() == "side" or \
                any(isinstance(c, str) and c.lower() in SIDE_WORDS for c in cells):
            out.append(d.name)
    return out


# ------------------------------------------------------------------------------------------------ the declaration


def _int(x: Any, what: str) -> int:
    if not isinstance(x, int) or isinstance(x, bool):
        raise SpecRefused(f"{what} is an explicit integer, got {x!r}")
    return int(x)


def _ints(xs: Any, what: str) -> tuple[int, ...]:
    if not isinstance(xs, list) or not xs:
        raise SpecRefused(f"{what} is a list of integers")
    return tuple(_int(x, what) for x in xs)


def _pos(x: Any, what: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not (math.isfinite(x) and x > 0):
        raise SpecRefused(f"{what} is a finite number above zero, got {x!r}")
    return float(x)


@dataclass(frozen=True)
class Spec:
    """The declaration's survey numbers (its survey-spec block), checked."""

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
    dims: tuple[Mapping[str, Any], ...]
    limits: tuple[Mapping[str, Any], ...]
    check_level: float
    baselines: tuple[str, ...]
    baseline_seed: int
    candidates: int
    reread_seeds: tuple[int, ...]
    margin: float
    z: float
    no_harm_margin: float
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
        if want is None:
            continue
        if not isinstance(s[k], dict) or set(s[k]) != set(want):
            got = sorted(s[k]) if isinstance(s[k], dict) else type(s[k]).__name__
            raise SpecRefused(f"survey-spec {k} holds exactly {sorted(want)}, got {got}")
    pid = s["prereg_id"]
    if not isinstance(pid, str) or not re.fullmatch(r"F-\d+", pid):
        raise SpecRefused(f"a search is declared as a family F-NN, got {pid!r}")
    sv, rd, pr, lm, bl, fi, pl = (s[k] for k in ("survey", "rounds", "protocol", "limits", "baselines", "finalists",
                                                 "plateau"))
    if not isinstance(lm["list"], list):
        raise SpecRefused("survey-spec limits.list is a list (empty for none)")
    for lim in lm["list"]:
        if not isinstance(lim, dict) or set(lim) != {"measure", "key", "bound", "direction"} or \
                lim["direction"] not in ("<=", ">="):
            raise SpecRefused(f"a limit is {{measure, key, bound, direction <= or >=}}, got {lim!r}")
    dims = s["composite"]["dims"]
    if not isinstance(dims, list) or not dims:
        raise SpecRefused("the composite has at least one dimension")
    for d in dims:
        if not isinstance(d, dict) or set(d) != {"key", "lo", "hi", "direction", "weight"} or \
                not float(d["hi"]) > float(d["lo"]) or d["direction"] not in (1, -1) or float(d["weight"]) < 0:
            raise SpecRefused(f"a composite dimension is {{key, lo < hi, direction +1 or -1, weight >= 0}}: {d!r}")
    if not isinstance(bl["names"], list) or tuple(bl["names"]) != BASELINES:
        raise SpecRefused(f"the baselines are exactly {BASELINES} (CHARTER 3.8 (b)), got {bl['names']!r}")
    seeds, reread = _ints(pr["seeds"], "a protocol seed"), _ints(fi["reread_seeds"], "a re-read seed")
    if len(reread) < MIN_REREAD_SEEDS or len(set(reread)) != len(reread):
        raise SpecRefused(f"at least {MIN_REREAD_SEEDS} distinct re-read seeds, got {len(reread)}")
    if set(seeds) & set(reread):
        raise SpecRefused("the re-read seeds are fresh: disjoint from the selection seeds")
    if not isinstance(pl["rule"], dict):
        raise SpecRefused("the plateau rule is an object of PlateauRule's fields")
    parts = s["parts"]
    for k in PART_NAMES:
        b = parts[k]
        if not isinstance(b, dict) or not {"id", "sha256"} <= set(b) or \
                not re.fullmatch(r"[0-9a-f]{64}", str(b["sha256"])):
            raise SpecRefused(f"the part {k} is bound by its id and sha256, got {b!r}")
    lvl = _pos(lm["check_level"], "the limits' one-sided check level")
    if lvl >= 0.5:
        raise SpecRefused("the limits' check level is below one half")
    out = Spec(raw=s, prereg_id=pid, survey_n=_int(sv["n"], "the survey size"), method=str(sv["method"]),
               survey_seed=_int(sv["seed"], "the survey seed"),
               max_proposals=_int(sv["max_proposals"], "max_proposals"),
               rounds=_int(rd["count"], "the rounds' count"), round_seed=_int(rd["seed"], "the rounds' seed"),
               round_kw={k: rd[k] for k in ROUND_KEYS}, measure=str(pr["measure"]),
               blocks=tuple((str(b[0]), str(b[1])) for b in pr["blocks"]), seeds=seeds,
               horizon=_int(pr["horizon"], "the horizon"), dims=tuple(dims), limits=tuple(lm["list"]),
               check_level=lvl, baselines=BASELINES, baseline_seed=_int(bl["seed"], "the baselines' seed"),
               candidates=_int(fi["candidates"], "the candidates' count"), reread_seeds=reread,
               margin=_pos(fi["margin"], "the finalists' margin (the size that matters)"),
               z=_pos(fi["z"], "the finalists' z"),
               no_harm_margin=float(s["no_harm"]["margin"]), plateau_rule=dict(pl["rule"]),
               plateau_seed=_int(pl["seed"], "the plateau seed"),
               plateau_box_seed=None if pl["box_seed"] is None else _int(pl["box_seed"], "the box seed"),
               parts=dict(parts))
    if not (math.isfinite(out.no_harm_margin) and out.no_harm_margin >= 0):
        raise SpecRefused("the no-harm margin is finite and non-negative")
    if out.rounds < 0 or out.candidates < 1 or out.survey_n < 1:
        raise SpecRefused("the rounds a count, the survey and the candidates at least one")
    return out


def fixture_pin(path: Path | str) -> str:
    """A test's stand-in for a pin: honoured only outside `prereg/` and outside any `results/` folder."""
    return FIXTURE_PREFIX + _file_sha(path)


def _inside(p: Path, d: Path) -> bool:
    try:
        p.resolve().relative_to(d.resolve())
        return True
    except ValueError:
        return False


def check_pinned(path: Path, sha: str, spec: Spec, *, results_dir: Path, pin_fixture: str | None) -> str:
    """The pin's decision row ("fixture" under a fixture pin) when the declaration is pinned (the module docstring),
    else `NotPinned`. The decision log is this repository's (`ROOT`) only (m-5)."""
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
    if not SEARCH_DECLARATION.fullmatch(rel):
        raise NotPinned(f"REFUSED: a search's declaration is prereg/F-NN_<name>.md, not {rel}")
    if not rel.startswith(f"prereg/{spec.prereg_id}_"):
        raise NotPinned(f"REFUSED: the spec's id {spec.prereg_id} is not the file's ({rel})")
    if not _inside(results_dir, ROOT):
        raise NotPinned(f"REFUSED: a pinned survey writes inside this repository's tree, not {results_dir}")
    dec = ROOT / "DECISIONS.md"
    text = dec.read_text(encoding="utf-8") if dec.is_file() else ""
    pinned = R.pins(text).get(rel)
    if not pinned:
        raise NotPinned(f"REFUSED: {rel} is not pinned: no decision row carries its sha256 (the lead pins a "
                        "declaration before its survey)")
    if pinned != {sha}:
        raise NotPinned(f"REFUSED: {rel} hashes to {sha[:12]}, its pin is {sorted(h[:12] for h in pinned)}: a change "
                        "is a new declaration")
    for line in text.splitlines():
        m = R.ROW.match(line)
        if m and f"`{rel}` sha256 `{sha}`" in line:
            return m.group(1)
    raise NotPinned(f"REFUSED: {rel}'s pin is in no decision row")


# ------------------------------------------------------------------------------------------------ scoring


def composite_score(dims: Sequence[Mapping[str, Any]]) -> Callable[[Mapping[str, Any]], np.ndarray]:
    """The composite per seed from the spec's dimensions, higher better: C(c) = sum_d w_d mean_s z_d(s, c),
    z_d = clip((x - lo) / (hi - lo), 0, 1), flipped for a lower-is-better dimension (`extended/wave42.py`'s form)."""
    ds = [dict(d) for d in dims]

    def score(arm: Mapping[str, Any]) -> np.ndarray:
        c: Any = 0.0
        for d in ds:
            x = np.asarray(arm[d["key"]], float)
            u = np.clip((x - float(d["lo"])) / (float(d["hi"]) - float(d["lo"])), 0.0, 1.0)
            z = u if d["direction"] > 0 else 1.0 - u
            c = c + float(d["weight"]) * z.mean(axis=0)
        return np.asarray(c, float)
    return score


def limit_values(arm: Mapping[str, Any], key: str) -> np.ndarray:
    """A limit measure per seed: its key's mean over the starts."""
    return np.asarray(arm[key], float).mean(axis=0)


# ------------------------------------------------------------------------------------------------ the context


@dataclass
class Context:
    spec: Spec
    parts: Parts
    E: Engine
    ledger: Any
    protocol: Any
    limits: tuple[Any, ...]
    sha: str
    rows: list[dict[str, Any]] = field(default_factory=list)
    readings: list[Any] = field(default_factory=list)                      # the objective's, searched cells
    limit_readings: dict[str, list[Any]] = field(default_factory=dict)
    rounds: list[Any] = field(default_factory=list)
    records: list[dict[str, Any]] = field(default_factory=list)
    memo: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = field(default_factory=dict)

    @property
    def score(self) -> Callable[[Mapping[str, Any]], np.ndarray]:
        return composite_score(self.spec.dims)


def new_ledger(E: Engine) -> Any:
    """The run's one cell ledger: the engine's own, whose survey role declares the protocol."""
    return E.SS.CellLedger()


def protocol_digest(p: Any) -> str:
    return _digest({"measure": p.measure, "blocks": [list(b) for b in p.blocks], "seeds": list(p.seeds),
                    "horizon": p.horizon, "libs": [list(x) for x in p.libs]})


def _check_output(ctx: Context, out: Any, protocol: Any) -> None:
    """The run's report on the protocol it was given, the design and every baseline paired (the same starts)."""
    if type(out) is not RunOutput:
        raise SurveyRefused(f"the runner reports a RunOutput, got {type(out).__name__}")
    if tuple(out.seeds) != tuple(protocol.seeds) or tuple(tuple(b) for b in out.blocks) != tuple(protocol.blocks) \
            or out.horizon != protocol.horizon:
        raise SurveyRefused("the runner ran off the protocol it was given (seeds, blocks or horizon)")
    missing = [a for a in (DESIGN_ARM,) + ctx.spec.baselines if a not in out.arms]
    if missing or set(out.real_path) != {AS_TRADED, REFLECTED}:
        raise SurveyRefused(f"the runner reports the design's and every baseline's arm and the real path's two "
                            f"readings; missing {missing or sorted({AS_TRADED, REFLECTED} - set(out.real_path))}")
    shapes = {np.asarray(x).shape for arm in list(out.arms.values()) + list(out.real_path.values())
              for x in arm.values()}
    if len(shapes) != 1 or next(iter(shapes))[-1:] != (len(protocol.seeds),):
        raise SurveyRefused(f"every arm on the same starts and one column a seed (paired), got shapes {sorted(shapes)}")


def book_check(out: RunOutput) -> None:
    """Every position of the run into one user's book (`components.UserBook`): two opposite positions at once across
    the user's accounts or firms are conduct tier 1, two at once an undefined overlap (m-2): `_Refused` either way."""
    from extended import components as C

    book = C.UserBook()
    try:
        book.extend(out.positions)
    except C.TierOneRefused as e:
        raise _Refused("tier1", str(e)) from e
    except C.OverlapRefused as e:
        raise _Refused("overlap", str(e)) from e


def gate_check(ctx: Context, out: RunOutput) -> None:
    """The declared gate (supply, resolution, realised risk) before any measure: `_Refused` with its reason."""
    why = ctx.parts.gate(out)
    if why:
        raise _Refused("gate", str(why))


def screen(ctx: Context, out: RunOutput) -> None:
    """Before any measure is read: the user's book (conduct tier 1), then the gate."""
    book_check(out)
    gate_check(ctx, out)


def _reading(ctx: Context, design: Mapping[str, Any], per: Any, out: RunOutput, measure: str, reread: bool,
             roles: Callable[[str], bool]) -> Any:
    SS = ctx.E.SS
    per = np.asarray(per, float).ravel()
    se = float(per.std(ddof=1) / math.sqrt(len(per))) if len(per) > 1 else 0.0
    r = SS.Reading(dict(design), float(per.mean()), tuple(out.blocks), tuple(out.seeds), str(out.tag), measure,
                   out.horizon, se, tuple(per))
    return SS.admit_one(r, ledger=ctx.ledger, measure=measure, reread=reread, roles=roles)


def _any(role: str) -> bool:
    return True


def _row(ctx: Context, role: str, design: Mapping[str, Any], measure: str, r: Any, refused: str = "") -> None:
    ctx.rows.append({"role": role, "id": ctx.E.SS.design_id(design), "measure": measure,
                     "value": None if r is None else float(r.value), "se": None if r is None else float(r.se),
                     "per_seed": "" if r is None else json.dumps(list(r.per_seed)), "refused": refused,
                     "design": json.dumps(dict(design), sort_keys=True, default=str)})


def read_design(ctx: Context, design: Mapping[str, Any], protocol: Any, role: str) -> dict[str, Any]:
    """Steps 3-5 (the module docstring): {measure: Reading} for the design, `BASELINE_ROLE`: {baseline: Reading} on
    the same run, `"out"`: the run; `_Refused` when the book or the gate refuses."""
    reread = tuple(protocol.seeds) != tuple(ctx.protocol.seeds)
    key = (ctx.E.SS.design_id(design), tuple(protocol.seeds))
    if key in ctx.memo:
        return ctx.memo[key]
    out = ctx.parts.runner(ctx.parts.build_schedule(dict(design)), protocol)
    _check_output(ctx, out, protocol)
    try:
        screen(ctx, out)
    except _Refused as g:
        _row(ctx, role, design, "", None, f"{g.cls}: {g.reason}")
        raise
    m = ctx.spec.measure
    got: dict[str, Any] = {m: _reading(ctx, design, -ctx.score(out.arms[DESIGN_ARM]), out, m, reread, _any)}
    if not reread:
        for lim in ctx.spec.limits:
            got[lim["measure"]] = _reading(ctx, design, limit_values(out.arms[DESIGN_ARM], lim["key"]), out,
                                           lim["measure"], False, _any)
    got[BASELINE_ROLE] = {b: _reading(ctx, {"baseline": b}, -ctx.score(out.arms[b]), out, m, reread,
                                      lambda r: r == BASELINE_ROLE) for b in ctx.spec.baselines}
    got["out"] = out
    for k, r in got.items():
        if k not in (BASELINE_ROLE, "out"):
            _row(ctx, role, design, k, r)
    ctx.memo[key] = got
    return got


def _keep(ctx: Context, got: Mapping[str, Any]) -> None:
    ctx.readings.append(got[ctx.spec.measure])
    for lim in ctx.spec.limits:
        ctx.limit_readings.setdefault(lim["measure"], []).append(got[lim["measure"]])


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
    return ctx.E.SS.Sampler(ctx.parts.space, seed=s.survey_seed, method=s.method).survey(
        s.survey_n, ledger=ctx.ledger, protocol=ctx.protocol, reread_seeds=s.reread_seeds,
        measures=tuple(lim["measure"] for lim in s.limits), max_proposals=s.max_proposals)


def run_rounds(ctx: Context) -> None:
    """Step 6: exactly the declared rounds, each proposed from the surrogate and read."""
    P = ctx.E.P
    spec = P.RoundSpec(**ctx.spec.round_kw)
    for i in range(1, ctx.spec.rounds + 1):
        rnd = P.propose(ctx.parts.space, ctx.readings, spec=spec, round_index=i, seed=ctx.spec.round_seed,
                        ledger=ctx.ledger, limits=ctx.limits,
                        limit_readings=dict(ctx.limit_readings) if ctx.limits else None)
        ctx.rounds.append(rnd)
        read_all(ctx, rnd.designs, f"round-{i}")


def finalist_candidates(ctx: Context) -> list[Any]:
    """The finalist order rule: the read searched cells by selection reading, lowest first (ties by id), the first
    `candidates`."""
    seen: dict[str, Any] = {}
    for r in ctx.readings:
        seen.setdefault(r.id, r)
    return sorted(seen.values(), key=lambda r: (float(r.value), r.id))[:ctx.spec.candidates]


def beats_baselines(ctx: Context, got: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    """On the re-read: each baseline's paired gap (baseline - candidate, minimised units) past the margin at z."""
    mine = np.asarray(got[ctx.spec.measure].per_seed, float)
    gaps, ok = {}, True
    for b in ctx.spec.baselines:
        diff = np.asarray(got[BASELINE_ROLE][b].per_seed, float) - mine
        d = float(diff.mean())
        se = float(diff.std(ddof=1) / math.sqrt(len(diff)))
        z = (d - ctx.spec.margin) / se if se > 0 else (math.inf if d > ctx.spec.margin else -math.inf)
        gaps[b] = {"gap": d, "se": se, "z": z, "beaten": bool(z > ctx.spec.z)}
        ok = ok and gaps[b]["beaten"]
    return ok, {"gaps": gaps}


def limits_inside(ctx: Context, sel: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    """E-230: each limit's point estimate (its selection reading) inside its bound decides; the one-sided check of
    crossing at the declared level is reported beside, never deciding (m-2)."""
    crit = NormalDist().inv_cdf(1.0 - ctx.spec.check_level)
    out, ok = {}, True
    for lim in ctx.spec.limits:
        r = sel[lim["measure"]]
        v, b = float(r.value), float(lim["bound"])
        inside = v <= b if lim["direction"] == "<=" else v >= b
        over = (v - b) if lim["direction"] == "<=" else (b - v)
        z = over / float(r.se) if r.se else (math.inf if over > 0 else -math.inf)
        out[lim["measure"]] = {"value": v, "bound": b, "direction": lim["direction"], "inside": inside,
                               "check_z": z, "check_level": ctx.spec.check_level, "crossing_shown": bool(z > crit)}
        ok = ok and inside
    return ok, {"limits": out}


def no_harm(ctx: Context, out: RunOutput) -> tuple[bool, dict[str, Any]]:
    """O-4's floor: the sides come from the design's own trigger, and its real-path as-traded composite is no worse
    than the reflected (coin) composite by more than the declared margin (point estimate, CHARTER 3.8 (c))."""
    d = float(np.mean(ctx.score(out.real_path[AS_TRADED]) - ctx.score(out.real_path[REFLECTED])))
    held = out.side_source == TRIGGER and d >= -ctx.spec.no_harm_margin
    return held, {"no_harm": {"side_source": out.side_source, "as_traded_minus_reflected": d,
                              "margin": ctx.spec.no_harm_margin, "held": bool(held)}}


def plateau_step(ctx: Context, finalist: Any) -> Any:
    """`plateau.check` on the ledger's re-read seeds; a neighbour refused by the book or the gate refuses the
    candidate (raised as `_Refused`)."""
    PL = ctx.E.PL
    rule = PL.PlateauRule(**ctx.spec.plateau_rule)

    def evaluate(design: Mapping[str, Any], *, protocol: Any) -> Any:
        return read_design(ctx, design, protocol, "plateau")[ctx.spec.measure]

    return PL.check(finalist, ctx.parts.space, rule, evaluate, ledger=ctx.ledger, ledger_seed=ctx.spec.plateau_seed,
                    seed=ctx.spec.plateau_box_seed)


def choose_finalists(ctx: Context) -> list[dict[str, Any]]:
    """Step 7 (the module docstring): the finalists in order; every candidate's record in `ctx.records`."""
    SS = ctx.E.SS
    finalists = []
    sel: dict[str, dict[str, Any]] = {}
    for r in ctx.readings:
        sel.setdefault(r.id, {ctx.spec.measure: r})
    for m, rs in ctx.limit_readings.items():
        for r in rs:
            sel[r.id].setdefault(m, r)
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
                 ("every limit inside", limits_inside(ctx, sel[cand.id])),
                 ("the no-harm floor", no_harm(ctx, got["out"])))
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
    if ctx.parts.writer is not None:
        w = ctx.parts.writer
    else:
        from extended.results import write_result as w
    return w, (ctx.parts.variants_writer or vendored_variants_writer)


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
             "detail": json.dumps({k: r[k] for k in ("gaps", "limits", "no_harm", "plateau") if k in r},
                                  sort_keys=True, default=str)} for r in ctx.records]
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
                     "rounds, the re-reads and the plateau checks (search years only)", **common)
    cpath, _ = write(_records_frame(ctx), f"{name}_candidates", description=f"{ctx.spec.prereg_id}: every "
                     "candidate of the finalist order rule, in rank order, kept or refused and why", **common)
    out = []
    for i, f in enumerate(finalists, 1):
        text = (ctx.parts.playbook(f["design"]) if ctx.parts.playbook is not None else "").replace("\r\n", "\n")
        out.append({"order": i, "id": f["id"], "design": json.dumps(f["design"], sort_keys=True, default=str),
                    "selection_value": f["selection_value"], "reread_value": f["reread_value"],
                    "gaps": json.dumps(f["gaps"], sort_keys=True), "limits": json.dumps(f["limits"], sort_keys=True),
                    "no_harm": json.dumps(f["no_harm"], sort_keys=True), "plateau_rule": f["plateau"]["rule"],
                    "plateau_reason": f["plateau"]["reason"], "playbook": text,
                    "playbook_sha256": hashlib.sha256(text.encode()).hexdigest() if text else "",
                    "fit_sha256": json.dumps(fits)})
    cols = ["order", "id", "design", "selection_value", "reread_value", "gaps", "limits", "no_harm", "plateau_rule",
            "plateau_reason", "playbook", "playbook_sha256", "fit_sha256"]
    lpath, _ = write(pd.DataFrame(out, columns=cols), f"{name}_finalists",
                     description=f"{ctx.spec.prereg_id}: the finalists' list in the declared order (the finalist "
                     "order rule; empty when none)", **common)
    lsha = _file_sha(lpath)
    vpath = vwrite(rows, results_dir)                       # last: no counted rows without their results
    token = f"heldout-finalists: {ctx.spec.prereg_id} @ {ctx.sha} list {lsha}" if out else None
    return {"variants": Path(vpath), "readings": Path(rpath), "candidates": Path(cpath), "list": Path(lpath),
            "list_sha256": lsha, "token": token, "fit_sha256": fits}


def emit_failure(ctx: Context, exc: BaseException, *, params: Mapping[str, Any], results_dir: Path,
                 name: str) -> None:
    """m-4: a refusal after the survey's first cell -- the failure record (with the candidates so far), then the
    variants rows."""
    import pandas as pd

    write, vwrite = _writers(ctx)
    rows = variant_rows(ctx)
    common = _common(ctx, dict(params, counts=ctx.ledger.counts(), failed=type(exc).__name__), results_dir)
    df = pd.DataFrame([{"exception": type(exc).__name__, "message": str(exc)[:2000],
                        "counts": json.dumps(ctx.ledger.counts(), sort_keys=True),
                        "candidates": _records_frame(ctx).to_json(orient="records")}])
    write(df, f"{name}_failure", description=f"{ctx.spec.prereg_id}: the survey refused after its first cell; "
          "its record and the counts (its variants rows written after it)", **common)
    vwrite(rows, results_dir)


# ------------------------------------------------------------------------------------------------ the driver


@dataclass
class Outcome:
    declaration_sha256: str
    pin_row: str
    finalists: list[dict[str, Any]]
    candidates: list[dict[str, Any]]
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


def run_survey(declaration: Path | str, parts: Parts, *, results_dir: Path | str, name: str,
               pin_fixture: str | None = None) -> Outcome:
    """The whole loop (the module docstring): refusals first, then steps 2-8."""
    path, out_dir = Path(declaration), Path(results_dir)
    if not path.is_file():
        raise NotPinned(f"REFUSED: the declaration {path} does not exist")
    raw = path.read_bytes()                                                # read once: hashed and parsed (n-3)
    sha = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    spec = load_spec(raw)
    pin_row = check_pinned(path, sha, spec, results_dir=out_dir, pin_fixture=pin_fixture)
    if pin_fixture is None and any(x is not None for x in (parts.engine, parts.writer, parts.variants_writer)):
        raise PartRefused("REFUSED: under a pin the engine and the writers are this repository's own; an injected "
                          "one is honoured only under a fixture pin")
    if parts.gate is None or not callable(parts.gate):
        raise PartRefused("REFUSED: the gate is required (supply, resolution, realised risk; O-4's floor follows)")
    E = parts.engine or Engine.default()
    E.check()
    bound = bindings(parts, E)
    off = [k for k in PART_NAMES if bound[k] != spec.parts[k]]
    if off:
        raise PartRefused(f"REFUSED: the part(s) {off} differ from the declaration's binding (S-3): "
                          + "; ".join(f"{k} declared {spec.parts[k]}, given {bound[k]}" for k in off))
    sides = side_levers(parts.space)
    if sides:
        raise PartRefused(f"REFUSED: the searched lever(s) {sides} set a side; the side is the trigger's (O-4)")
    protocol = E.SS.Protocol(spec.measure, spec.blocks, spec.seeds, spec.horizon)       # refuses held-out blocks
    bad = heldout_problems(_existing_rows(out_dir / "variants.jsonl"))
    if bad:
        raise HeldOutRow(f"REFUSED: the variants ledger in {out_dir} already holds a held-out row: {bad[:3]}")
    limits = tuple(E.P.Limit(str(x["measure"]), float(x["bound"]), str(x["direction"])) for x in spec.limits)
    ctx = Context(spec, parts, E, new_ledger(E), protocol, limits, sha)
    params = {"declaration_sha256": sha, "pin_row": pin_row, "protocol_sha256": protocol_digest(protocol),
              "spec": spec.raw, "bindings": bound, "round_spec": asdict(E.P.RoundSpec(**spec.round_kw)),
              "task": TASK}
    try:
        designs = draw_survey(ctx)
        if protocol_digest(ctx.ledger.protocol) != protocol_digest(protocol) or \
                tuple(ctx.ledger.reread.seeds) != spec.reread_seeds:
            raise SurveyRefused("the ledger's protocol is not the pinned declaration's (rb2-a)")
        ctx.ledger.begin(BASELINE_ROLE, spec.baseline_seed)
        for b in spec.baselines:
            ctx.ledger.record(parts.space, {"baseline": b}, role=BASELINE_ROLE, seed=spec.baseline_seed, refusal=None)
        read_all(ctx, designs, "survey")
        run_rounds(ctx)
        finalists = choose_finalists(ctx)
        em = emit(ctx, finalists, params=params, results_dir=out_dir, name=name)
    except Exception as exc:
        if ctx.ledger.rows:
            try:
                emit_failure(ctx, exc, params=params, results_dir=out_dir, name=name)
            except Exception as e2:                                        # the original refusal is the one raised
                exc.add_note(f"the failure record could not be written: {type(e2).__name__}: {e2}")
        raise
    return Outcome(sha, pin_row, finalists, list(ctx.records), em["token"], em["list"], em["list_sha256"],
                   em["readings"], em["candidates"], em["variants"], ctx.ledger.counts(), ctx.ledger, ctx.rounds,
                   bound)


__all__ = ["TASK", "ENGINE_COMMIT", "DESIGN_ARM", "BASELINE_ROLE", "BASELINES", "MIN_REREAD_SEEDS", "AS_TRADED",
           "REFLECTED", "TRIGGER", "FIXTURE_PREFIX", "PART_NAMES", "SurveyRefused", "NotPinned", "SpecRefused",
           "PartRefused", "HeldOutRow", "RunOutput", "Engine", "Parts", "Spec", "Context", "Outcome",
           "part_binding", "space_digest", "engine_binding", "bindings", "side_levers", "load_spec", "fixture_pin",
           "check_pinned", "composite_score", "limit_values", "new_ledger", "protocol_digest", "book_check", "gate_check", "screen",
           "read_design", "read_all", "draw_survey", "run_rounds", "finalist_candidates", "beats_baselines",
           "limits_inside", "no_harm", "plateau_step", "choose_finalists", "heldout_problems",
           "vendored_variants_writer", "variant_rows", "emit", "emit_failure", "run_survey"]
