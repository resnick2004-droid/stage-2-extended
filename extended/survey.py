"""Wave 5 (the restart plan, Waves 5-6; CHARTER 3.3, 3.5, 3.6, 3.8, 3.9; the design-search template's sections 6, 7
and 14): the survey runner -- the end-to-end driver of one declared design search, on the search years only.

    python scripts/survey_run.py prereg/F-NN_<name>.md          # under a pin: the one entry, inside a clean run
    SV.run_survey(path, results_dir=..., name=..., pin_fixture=SV.fixture_pin(path), ...)   # a test's fixture pin

**Nothing is injected** (F-2): the declaration names every part -- the lever space, the gate, the schedule builder,
the three-way runner, the playbook writer -- by a factory id (`module:function`), its parameters and every data file
it reads (each by sha256); the survey builds each part itself (`build_part`). A part is **bound** by the sha256 of its
id, parameters, gate keys, data and code (its module and every `extended` module it imports, transitively); the
space's built digest is compared too, and the engine (Wave 3.4 with Q-192, `search_space`, `surrogate`, `proposer`,
`plateau`) and the objective's code are bound the same way: `objective.code_sha256` covers `extended.wave42_r2`,
`extended.wave42` and `extended.search_calendar`, **the driver itself** (`extended.survey`'s closure), the entry
script `scripts/survey_run.py` and W42-R2's application script, each compared, never only recorded (Q-186 m-4). **Under a
pin** the process is the entry script inside a clean run, invoked as exactly `python scripts/survey_run.py
prereg/F-NN_<name>.md` -- no `-c`, `-m`, `-i`, `-X` or any other flag, not interactive, no `PYTHONSTARTUP`,
`PYTHONINSPECT` or `PYTHONPATH` (`invocation_problems`, so a `runpy` wrapper refuses) -- the tree clean counting
untracked files (only git-ignored ones allowed), every bound module a tracked file of this repository, the results
folder `ROOT/results`, and the commit and the entry script's sha256 recorded (M-4).

**Data** (Q-186 M-1): a declared data file is a path inside the repository by its **unresolved** path (normalised
lexically, `os.path.abspath`), and the only links it may pass through are the two junctions every clean checkout makes
to the licensed data, `scripts/worktrees.py`'s `STORES` (`vendor/stage2/data/bars`, `vendor/stage2/data/atlas`;
Q-186b F-1); a symlink or junction anywhere else refuses, and so does a `:` anywhere in the path (an NTFS stream, n-a).
The runner's reported `data` equals the runner's declared data key for key (a missing key refuses, an extra key
refuses). It is still the runner's own report: its own identity must cover its data report (a runner that declares
and reports nothing passes `{} == {}`; Q-186b n-b).

**One objective, W42-R2's** (C-1; E-296, E-299: W42-R2 is the setting rule applied to H4, W42-R1 is never applied):
the rule the survey calls (`_wave42()`, an `ObjectiveRule`) is W42-R2's module for its tables and limits
(`W42_R2_NAMES`: `wave42_r2.RULE_ID`, `OUTPUT_NAME`, `LIMITS`, `REQUIRED`, `HORIZONS`, `limit_estimate`,
`limit_check`, ... -- the headroom-corrected limits and the floor on the median `net_month_12`) and, for every other
name, W42-R1's module, whose code W42-R2 runs unchanged (the composite, the do-nothing journey and floor, delta*, the
calendars). The survey reads `results/` + `wave42_r2.OUTPUT_NAME` (its `key` / `value_json` rows) by name, checks its
sidecar (its file sha256, `scripts/wave42_r2_apply.py`, the rule id, the values' digest, the rule module's raw-bytes
sha256 -- `extended/wave42_r2.py`'s -- equal to this tree's) and, under a pin, the decision row that pins its sha256.
The composite and every limit are the rule's own public functions (`composite_per_seed`, W42-R2's `limit_estimate`),
never re-implemented here; the do-nothing floor is `null_journeys.floor`, self-checked at load against the public
composite of `wave42.null_journeys(...)["do_nothing"]`, and decided by W42-R1's own comparator `wave42.above_floor`,
which W42-R2 carries (Q-186 m-1); the one-sided check beside each limit is W42-R2's `limit_check` (normal z, B-10's
form; Q-186 n-1). Every limit W42-R2 declares must be `set` (m-2); its `inactivity_guards` and each limit's vacuous
flag are written beside the candidates. **Under a pin the values file's provenance is checked** (Q-186 m-3, Q-186b
F-2): its `parameters.pinned_commit` is 40 hex and equals this checkout's pin (`wave42_r2_apply.pinned_commit(ROOT)`,
`config/w42_r2_pin.json`), its `git_commit` is 40 hex and clean (no `-dirty`), names a commit of this repository
(`git cat-file -e`) that is an ancestor of the run's HEAD, and `wave42_r2_apply.commit_problem(ROOT, pinned_commit,
head=git_commit)` is None (the pinned commit, or a descendant touching none of W42-R2's imported files, W42-R1's
among them); and `extended.results.verify_result` passes. (That import puts the vendored
tree at the front of `sys.path` for the rest of the process: from then on a bare import in any part resolves to the
vendored scripts first; every import of the survey's own is qualified `extended.`.) A malformed sidecar refuses as
`SpecRefused` (n-5). The no-harm margin is the declaration's (`no_harm: {margin, margin_row}`): under a pin its row
exists, comes before the declaration's pin row, names the no-harm margin, and the **first number after that name**
(directly, or after `is`, `of`, `at`, `=` or `:`) is the margin itself -- a plain decimal, no sign, exponent or
percent, equal as a float (Q-186 m-2, Q-186b F-3); the values' row names `W42-R2` (not `W42-R20`) and
`w42_r2_values.csv` as a whole word and carries the file's sha256 as a whole 64-hex word.

**The calendar** (M-3): the runner reports each start's date; the survey checks every one against the pinned search
calendar (Q-197's `results/search_calendar.csv` through `extended.search_calendar.load_search_calendar`, its sha256
`wave42.SEARCH_CALENDAR_SHA256`, its dates the ones W42-R2 was set on) and the protocol's blocks, and computes each
start's sessions left itself, on W42-R1's definition (the calendar's sessions from the start to 2023-12-29, the start
counted): a start whose horizon needs a session after 2023-12-29 is incomplete. The runner's values are checked as
W42-R1 checks the baselines' (m-3): finite and inside `wave42.REQUIRED`'s ranges on each key's complete starts, and no
unit paid before its first pass.

**The loop** (each step a function, so a test can mutate it): `draw_survey` (the survey's `begin` checks the
protocol against the declaration's protocol sha256, Q-192); `read_design` (held-out first, F-4; then the report, the
book per path and the gate on its declared keys before any measure; the composite and limits through the door);
`run_rounds`; `choose_finalists` -- **the floors before ranking** (V-4, in order: the no-harm floor, the
`not_paid_within_B` limit, the do-nothing floor; a cell failing one is recorded, never ranked), the first `candidates`
by selection reading, each re-read on the fresh seeds and kept only if it beats each baseline by more than delta* on
the t law (F-7), every limit's re-read point estimate inside (F-3), the no-harm and do-nothing floors hold again, and
the plateau accepts it; `emit` (the readings, the candidates, the finalists' list, then the variants rows). **The
do-nothing floor is strict and not passed by rounding** (M-2): the composite (the float mean over seeds) must exceed
the floor by more than W42-R1's `DO_NOTHING_EPS` (1e-9, far above one rounding unit), decided by `above_floor` itself,
so the screen and the held-out verdict apply one comparator. A refusal after the first cell writes the variants rows
and then the failure record, each attempted (F-6).

**Once** (F-5, m-1, Q-186 m-5, Q-186b F-4): a second run of one declaration is refused -- by the outputs and the
variants ledger of its folder, by the decision log, and, under a pin, by a record **outside every checkout**: an
exclusive marker `%LOCALAPPDATA%/stage2-extended-runs/survey_once/<sha256>.json`, created with `O_CREAT | O_EXCL`
(atomic: of two runs started together exactly one creates it), and beside it the append-only log `survey_once.jsonl`
(`ONCE_FILE`), one line per run. Both are checked before the first refusal that reads the objective; the marker is
created and the line appended just before the first cell, and the line is printed at once, flushed, as
`survey-once: <line>` (so the clean run's log holds it even when the run then refuses or crashes; the lead's row quotes
it: a deleted record cannot be prevented, only made visible). Under a pin the runs folder is the Windows known folder (the
`LOCALAPPDATA` variable must equal `SHGetKnownFolderPath(FOLDERID_LocalAppData)`) and `run.lock` is held by this run
(`S2X_LOCK_HOLDER` equal to the lock's job). `run_clean.py --discard` and `--remove` touch only a checkout, never the
record. **A fixture-pinned run prints no finalists' token** (Q-186 m-6): its token is `survey-fixture-finalists: ...`,
which no held-out rule reads; and **a fixture pin builds no `extended.` part** (Q-186b F-5): a preview of a real
search on real parts is refused, so every real cell is counted by a pinned run.

**Requirements on the parts' builds** (the survey cannot enforce them; their own reviews must, Q-186 n-2, n-3):
- n-2, held-out reads: the survey sees the runner's tag, blocks, horizon, starts and `data` report, never its reads.
  The three-way runner reads bars only through `extended.reader.read_bars(start, end, ...)` with `end` at most
  2023-12-29 (a start late in 2023 walked 252 sessions must stop there, not read 2024), should report a per-start
  `reach` (the last bar date read) that the survey can refuse past `SEARCH_LAST`, and may, under a pin, install
  `sys.addaudithook` on `open` refusing any file outside the declared data and code.
- n-3, the baselines: nothing here ties the runner's naive-coin, P-14, P-15 and P-16 arms to H4's readings; the
  runner's own identity (CLAUDE.md: every new runner has its own identity) covers every baseline arm path for path,
  since every gap is measured against them.
- n-7: `wave42.SEARCH_CALENDAR_SHA256` (W42-R1's constant, read by W42-R2) is filled at W42-R1's pin; until then a
  real-pin run refuses at `load_calendar`, by design.
"""
from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
import math
import os
import re
import subprocess
import sys
import types
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from extended import CLEAN_RUN_ENV, ROOT, RUN_ID_ENV, RUNS_DIR
from extended import reader as R

TASK = "Wave 5"
ENGINE_COMMIT = "3452952"                               # Wave 3.4 with Q-192, Q-192b and rm3-b (1024 midpoints)
W42_RULE = "W42-R2"                                     # E-296, E-299: the rule applied to H4; W42-R1 never is
W42_SCRIPT = "scripts/wave42_r2_apply.py"                # W42-R2's application (pinned at 5ae351d, E-299)
ENTRY_SCRIPT = "scripts/survey_run.py"
DESIGN_ARM = "design"
BASELINE_ROLE = "baseline"
BASELINES = ("naive_coin", "p14", "p15", "p16")       # CHARTER 2, 3.8 (b): Topstep's baseline set (E-221)
AS_TRADED, REFLECTED = "as_traded", "reflected"
TRIGGER = "trigger"
SEARCH_TAG = "search"
SEARCH_LAST = "2023-12-29"
DELTA_STAR = "delta_star"
NOT_PAID = "not_paid_within_B"
DO_NOTHING = "do_nothing"
FLOOR_SELF_CHECK = 1e-12                                 # C-1: the floor against the public composite of do_nothing
W42_PUBLIC = ("composite_per_seed", "limit_estimate", "limit_check", "null_journeys", "do_nothing_floor",
              "above_floor", "values_from_rows", "calendar_digest")
SPEC_FENCE = re.compile(rb"^```survey-spec[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
FIXTURE_PREFIX = "survey-fixture-pin:"
FIXTURE_TOKEN = "survey-fixture-finalists:"            # m-6: a fixture run's token, which no held-out rule reads
REAL_TOKEN = "heldout-finalists:"                      # Q-158's form, emitted under a pin only
#: M-1: the only links a declared data file may pass through -- the clean checkout's junctions to the licensed data
DATA_LINKS = ("vendor/stage2/data/bars", "vendor/stage2/data/atlas")    # = scripts/worktrees.py STORES (F-1)
#: m-5: the append-only once-record, outside every checkout (a module attribute, so a test points it elsewhere)
ONCE_FILE = Path(RUNS_DIR) / "survey_once.jsonl"
#: m-4: the environment a pinned invocation runs without
INVOCATION_ENV = ("PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONPATH")
_HERE = Path(__file__).resolve().parents[1]           # the driver's own tree: the entry script's binding (m-4)
FIXTURE_ROW = "fixture"
SEARCH_DECLARATION = re.compile(r"prereg/F-\d+_[^/`]*\.md")
PART_NAMES = ("space", "gate", "schedule_builder", "runner", "playbook")
OUTPUTS = ("readings", "candidates", "finalists", "failure")
_HELD_OUT_WORDS = ("heldout", "judged", "holdout", "confirm")
_HELD_OUT_LABEL = re.compile(r"held[-_ ]?out|judged|confirmation", re.IGNORECASE)
_ISO = re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)")
_HEX64 = re.compile(r"[0-9a-f]{64}")
_ROW_ID = re.compile(r"E-(\d+)")

ROUND_KEYS = ("batch", "pool", "acquisition", "kappa", "xi", "centres", "local", "local_scale", "restarts",
              "p_feasible")
SPEC_KEYS: dict[str, tuple[str, ...] | None] = {
    "prereg_id": None,
    "survey": ("n", "method", "seed", "max_proposals"),
    "rounds": ("count", "seed") + ROUND_KEYS,
    "protocol": ("measure", "blocks", "seeds", "horizon", "sha256"),
    "objective": ("rule_id", "values_row", "code_sha256"),
    "baselines": ("names", "seed"),
    "finalists": ("candidates", "reread_seeds", "z"),
    "no_harm": ("margin", "margin_row"),
    "plateau": ("rule", "seed", "box_seed"),
    "parts": PART_NAMES + ("engine",),
}


class SurveyRefused(RuntimeError):
    """A survey this module cannot stand behind."""


class NotPinned(SurveyRefused):
    """The declaration is not pinned by a row of this repository's decision log (nor a test's fixture)."""


class SpecRefused(SurveyRefused):
    """The declaration's survey-spec block, or W42-R2's result, is missing, malformed or off its form."""


class PartRefused(SurveyRefused):
    """A part whose binding differs from the declaration's, or a part, engine or process the runner never accepts."""


class RunRepeated(SurveyRefused):
    """A second run of one declaration (F-5, m-1): results are never overwritten and a survey is run once."""


class HeldOutRow(SurveyRefused):
    """A variants row naming the held-out years or a held-out tag (CHARTER 3.3 (f))."""


class LimitDisagrees(SurveyRefused):
    """W42-R2's own `limit_check` reads a limit otherwise than the survey's reading (Q-186 n-1): not one limit."""


class _Refused(Exception):
    """A design refused at its read, before any measure (the book or the gate): its cell stays counted."""

    def __init__(self, cls: str, reason: str):
        super().__init__(f"{cls}: {reason}")
        self.cls, self.reason = cls, reason


# ------------------------------------------------------------------------------------------------ what a run reports


@dataclass(frozen=True)
class RunOutput:
    """The three-way runner's report for one design on one protocol: `starts` each start's date (ISO, on the search
    calendar, increasing); `arms[arm][key]` a start-by-seed matrix for `DESIGN_ARM` and each baseline, every key
    `wave42.REQUIRED` names and the gate's keys; `real_path[AS_TRADED | REFLECTED][key]` the design's real-path
    readings -- `AS_TRADED` its trigger's own sides, `REFLECTED` the coin side on the as-walked (reflected) path, same
    fills, same seeds (CHARTER 3.8's exception) -- never the deciding reading; `side_source` where the playbook's sides
    come from (`TRIGGER`); `positions[path]` every `components.Position` of one (start, seed) path, across the user's
    accounts and firms; `data` the sha256 of every data file the run read (path relative to the repository); the
    seeds, blocks and horizon it ran; its tag. Sessions left are never the runner's: the survey computes them."""

    starts: tuple[str, ...]
    arms: Mapping[str, Mapping[str, Any]]
    real_path: Mapping[str, Mapping[str, Any]]
    side_source: str
    positions: Mapping[str, Sequence[Any]]
    data: Mapping[str, str]
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
        """Refuse an engine without Q-192's API: the survey's `begin` checks the declaration's protocol sha256 and
        returns the role's pen; the doors take the ledger's protocol."""
        SS, PL = self.SS, self.PL
        for fn, names in ((SS.Sampler.survey, ("protocol", "reread_seeds", "measures", "declaration_sha256")),
                          (SS.admit_one, ("measure", "reread")),
                          (SS.CellLedger.begin, ("protocol", "reread_seeds", "measures", "declaration_sha256"))):
            if not all(n in inspect.signature(fn).parameters for n in names):
                raise PartRefused(f"the engine's {fn.__qualname__} lacks {names}: not Q-192's engine ({ENGINE_COMMIT})")
        if not all(hasattr(SS, n) for n in ("protocol_sha256", "RolePen")) or \
                "protocol" in inspect.signature(PL.check).parameters or \
                "reads_through" in {f.name for f in fields(SS.Reading)}:
            raise PartRefused(f"the engine is not Q-192's ({ENGINE_COMMIT}): no protocol sha256 or role pens, or the "
                              "doors take a caller's protocol")


# ------------------------------------------------------------------------------------------------ bindings


def _lf_sha(p: Any) -> str:
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _raw_sha(p: Any) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


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
    pkg = name if path.endswith("__init__.py") else name.rsplit(".", 1)[0]
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


def closure_files(module: str) -> dict[str, str]:
    """{module: its source file} for `module` and every `extended` module it imports, transitively."""
    seen: dict[str, str] = {}
    todo = [module]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        src = _origin(name)
        if src is None:
            raise PartRefused(f"the module {name!r} has no source file to bind")
        seen[name] = src
        todo += sorted(_imports(src, name) - set(seen))
    return dict(sorted(seen.items()))


def code_closure(module: str) -> dict[str, str]:
    """{module: LF sha256 of its file} over `closure_files(module)`."""
    return {k: _lf_sha(v) for k, v in closure_files(module).items()}


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
    """A part's binding: its factory id, canonical parameters, gate keys, declared data files (each by sha256), its
    space digest when declared, and its code closure."""
    pid = str(part["id"])
    return _digest({"id": pid, "params": _canon(part.get("params", {})), "keys": _canon(part.get("keys", [])),
                    "data": _canon(part.get("data", {})), "digest": part.get("digest"),
                    "code": code_closure(pid.partition(":")[0])})


def engine_sha(E: Engine) -> str:
    return _digest({m.__name__: code_closure(m.__name__) for m in E.modules().values()})


OBJECTIVE_MODULES = ("extended.wave42_r2", "extended.wave42", "extended.search_calendar")
DRIVER_MODULE = "extended.survey"


def driver_tree() -> Path:
    """The tree `extended.survey` was imported from (under a pin it must be the checkout: `check_process`)."""
    return _HERE


def entry_file() -> Path:
    """The entry script of the driver's own tree."""
    return _HERE / ENTRY_SCRIPT


def w42_script_file() -> Path:
    return _HERE / W42_SCRIPT


def objective_code() -> dict[str, Any]:
    """What `objective.code_sha256` binds (m-4): the objective's modules, the driver's own closure, the entry script
    and W42-R2's application script, each file by its LF sha256 (the application script `None` while it is not in the
    tree; a real pin then refuses at the values' provenance, which loads it)."""
    def lf(p: Path) -> str | None:
        return _lf_sha(p) if p.is_file() else None
    return {"objective": {m: code_closure(m) for m in OBJECTIVE_MODULES}, "driver": code_closure(DRIVER_MODULE),
            ENTRY_SCRIPT: lf(entry_file()), W42_SCRIPT: lf(w42_script_file())}


def objective_code_sha() -> str:
    return _digest(objective_code())


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


def _lexically_inside(p: Path | str, d: Path | str) -> bool:
    """`p` inside `d` by their unresolved paths, normalised lexically (`reader._under`'s convention): no link is
    followed, so a clean checkout's junctions to the licensed data stay inside it (Q-186 M-1)."""
    a, b = os.path.normcase(os.path.abspath(p)), os.path.normcase(os.path.abspath(d))
    return a.startswith(b.rstrip("\\/") + os.sep)


def _is_link(p: Path) -> bool:
    return os.path.islink(p) or bool(getattr(os.path, "isjunction", lambda _p: False)(p))


def data_path_problem(rel: Any, root: Path | None = None) -> str | None:
    """Q-186 M-1: None when `rel` (a relative path, `/`-separated) names a path inside `root` by its unresolved path,
    every link on the way one of `DATA_LINKS` where it stands; else what is wrong."""
    root = Path(ROOT if root is None else root)
    if not isinstance(rel, str) or not rel or "\\" in rel or os.path.isabs(rel) or Path(rel).drive:
        return "not a relative /-separated path"
    if ":" in rel:
        return "a ':' in the path (a drive or an NTFS stream)"
    parts = rel.split("/")
    if any(x in ("", ".", "..") for x in parts):
        return "an empty, '.' or '..' component"
    if not _lexically_inside(root / rel, root):
        return "outside the repository"
    for i in range(len(parts)):
        sub = "/".join(parts[:i + 1])
        if _is_link(root / sub) and sub not in DATA_LINKS:
            return f"passes through the link {sub} (only {list(DATA_LINKS)} may be links)"
    return None


def check_data(spec: "Spec") -> None:
    """Every data file a part declares is inside the repository by its unresolved path, passes through no link but
    the licensed data's two junctions (`data_path_problem`), exists and hashes (raw bytes) to its declared sha256."""
    for k in PART_NAMES:
        for rel, sha in spec.parts[k].get("data", {}).items():
            why = data_path_problem(rel)
            p = ROOT / str(rel)
            if why is None and not p.is_file():
                why = "missing"
            if why is None and _raw_sha(p) != sha:
                why = "not its declared sha256"
            if why is not None:
                raise PartRefused(f"REFUSED: the part {k}'s data file {rel}: {why} (M-4, Q-186 M-1)")


def check_bindings(spec: "Spec", E: Engine) -> dict[str, Any]:
    """Every binding recomputed and compared with the declaration's: the parts, the engine and the objective's code."""
    got = {k: part_sha(spec.parts[k]) for k in PART_NAMES}
    got["engine"] = engine_sha(E)
    got["objective_code"] = objective_code_sha()
    want = {k: spec.parts[k]["sha256"] for k in PART_NAMES}
    want["engine"] = spec.parts["engine"]["sha256"]
    want["objective_code"] = spec.raw["objective"]["code_sha256"]
    off = [k for k in got if got[k] != want[k]]
    if off:
        raise PartRefused(f"REFUSED: the binding(s) {off} differ from the declaration's (F-2): "
                          + "; ".join(f"{k} declared {want[k][:12]}, here {got[k][:12]}" for k in off))
    return got


def searched_levers() -> frozenset[str]:
    """The allowlist (F-8): the searched lever ids of the lever table. The side itself is a declared rule, never a
    lever; T1 (signal source) and T5 (entry type) choose the trigger and so its own side relative to a level -- the
    trigger's side, held by the no-harm floor -- which the declaration's red team reads (n-2)."""
    from extended import lever_space as LS
    return frozenset(k for k, v in LS.LEVERS.items() if v.cls == LS.SEARCHED)


def check_levers(space: Any) -> None:
    allowed = searched_levers()
    bad = [d.name for d in space.dims if str(getattr(d, "lever", "")) not in allowed]
    if bad:
        raise PartRefused(f"REFUSED: the dimension(s) {bad} are not searched levers of the lever table (an allowlist, "
                          "F-8)")


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
    """The built space's canonical digest (sets sorted: no hash-seed dependence), compared with the declared one."""
    return _digest(_space_canon(space))


# ------------------------------------------------------------------------------------------------ under a pin


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def tree_problems() -> list[str]:
    """M-4: every change in the tree, untracked files counted (only git-ignored files are allowed)."""
    r = _git("status", "--porcelain", "--untracked-files=all")
    if r.returncode:
        return [f"git status failed: {r.stderr.strip()[:200]}"]
    return [line[3:] for line in r.stdout.splitlines() if len(line) > 3]


def untracked_modules(modules: Sequence[str]) -> list[str]:
    """M-4: each bound module's file a tracked file of this repository (inside `ROOT`, in git's index)."""
    bad = []
    for m in modules:
        for name, src in closure_files(m).items():
            p = Path(src)
            if not _inside(p, ROOT):
                bad.append(f"{name} ({src}: outside the repository)")
                continue
            rel = p.resolve().relative_to(ROOT.resolve()).as_posix()
            if _git("ls-files", "--error-unmatch", rel).returncode:
                bad.append(f"{name} ({rel}: not tracked)")
    return bad


def invocation_problems(root: Path, declaration: Path, *, argv: Sequence[str] | None = None, flags: Any = None,
                        env: Mapping[str, str] | None = None) -> list[str]:
    """Q-186 m-4: what is wrong with the process's own invocation for a pinned survey (empty when nothing is):
    `sys.orig_argv` is exactly `[python, scripts/survey_run.py, <the declaration>]` (each normalised: the script
    against `root`'s entry script, the declaration as the entry script reads it, `root / arg`), so `-c` (a `runpy`
    wrapper), `-m`, `-i`, `-X` and every other flag refuse; not interactive or inspecting; no `PYTHONSTARTUP`,
    `PYTHONINSPECT` or `PYTHONPATH` in the environment."""
    argv = list(sys.orig_argv if argv is None else argv)
    flags = sys.flags if flags is None else flags
    env = os.environ if env is None else env
    out = []

    def same(a: Path | str, b: Path | str) -> bool:
        return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))
    bad_argv = len(argv) != 3 or argv[1].startswith("-") or argv[2].startswith("-") or \
        not same(argv[1], Path(root) / ENTRY_SCRIPT) or not same(Path(root) / argv[2], declaration)
    if bad_argv:
        out.append(f"the process was invoked as {argv[1:]!r}, not exactly [{ENTRY_SCRIPT!r}, <the declaration>] "
                   "(no -c, -m, -i, -X or other flag)")
    for f in ("interactive", "inspect"):
        if getattr(flags, f, 0):
            out.append(f"the interpreter's {f} flag is set")
    out += [f"{k} is set" for k in INVOCATION_ENV if env.get(k)]
    return out


def check_process(results_dir: Path, modules: Sequence[str], declaration: Path) -> dict[str, str]:
    """M-4: under a pin, the process is the entry script, invoked exactly (`invocation_problems`), inside a clean run
    of a clean tree, every bound module tracked, the results folder `ROOT/results`. Returns the commit and the entry
    script's sha256."""
    main = R._main_script()
    if main is None or main != (ROOT / ENTRY_SCRIPT).resolve():
        raise PartRefused(f"REFUSED: a pinned survey runs only as {ENTRY_SCRIPT} (its __main__ is {main}): no "
                          "in-process call, so no step can be patched (M-4)")
    inv = invocation_problems(ROOT, Path(declaration))
    if inv:
        raise PartRefused(f"REFUSED: a pinned survey is invoked as `python {ENTRY_SCRIPT} prereg/F-NN_<name>.md` "
                          f"and nothing else (Q-186 m-4): {inv}")
    try:
        R._clean_run(ROOT, "a pinned survey")
    except R.ReadRefused as e:
        raise PartRefused(f"REFUSED: a pinned survey runs inside a clean run: {e}") from e
    held = lock_problem()
    if held:
        raise PartRefused(f"REFUSED: a pinned survey runs under run.lock, held by this run (Q-186b F-4): {held}")
    where = localappdata_problem()
    if where:
        raise PartRefused(f"REFUSED: the runs folder is the Windows known folder's (Q-186b F-4): {where}")
    dirty = tree_problems()
    if dirty:
        raise PartRefused(f"REFUSED: under a pin the tree is clean, untracked files counted: {dirty[:5]}")
    bad = untracked_modules(modules)
    if bad:
        raise PartRefused(f"REFUSED: under a pin every bound module is a tracked file of this repository: {bad[:5]}")
    if results_dir.resolve() != (ROOT / "results").resolve():
        raise PartRefused(f"REFUSED: a pinned survey writes only under {ROOT / 'results'}, not {results_dir}")
    if os.path.normcase(str(driver_tree())) != os.path.normcase(str(ROOT.resolve())):
        raise PartRefused(f"REFUSED: the driver's tree {driver_tree()} is not the checkout {ROOT}: the bound entry "
                          f"script and {W42_RULE}'s script are the checkout's own (m-4)")
    return {"commit": R._commit(ROOT, "a pinned survey"), "entry_sha256": _raw_sha(main)}


# ------------------------------------------------------------------------------------------------ the declaration


def _int(x: Any, what: str) -> int:
    if not isinstance(x, int) or isinstance(x, bool):
        raise SpecRefused(f"{what} is an explicit integer, got {x!r}")
    return int(x)


def _ints(xs: Any, what: str) -> tuple[int, ...]:
    if not isinstance(xs, list) or not xs:
        raise SpecRefused(f"{what} is a list of integers")
    return tuple(_int(x, what) for x in xs)


def _num(x: Any, what: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise SpecRefused(f"{what} is a finite number, got {x!r}")
    return float(x)


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
    protocol_sha256: str
    baselines: tuple[str, ...]
    baseline_seed: int
    candidates: int
    reread_seeds: tuple[int, ...]
    z: float
    no_harm_margin: float
    margin_row: str
    values_row: str
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
    sv, rd, pr, bl, fi, pl, parts, nh, ob = (s[k] for k in ("survey", "rounds", "protocol", "baselines", "finalists",
                                                            "plateau", "parts", "no_harm", "objective"))
    if not isinstance(bl["names"], list) or tuple(bl["names"]) != BASELINES:
        raise SpecRefused(f"the baselines are exactly {BASELINES} (CHARTER 3.8 (b)), got {bl['names']!r}")
    seeds, reread = _ints(pr["seeds"], "a protocol seed"), _ints(fi["reread_seeds"], "a re-read seed")
    if len(set(reread)) != len(reread) or set(seeds) & set(reread):
        raise SpecRefused("the re-read seeds are distinct and fresh: disjoint from the selection seeds")
    z = _num(fi["z"], "the finalists' z")
    if not z > 0:
        raise SpecRefused(f"the finalists' z is above zero, got {z!r}")
    if not isinstance(pr["sha256"], str) or not _HEX64.fullmatch(pr["sha256"]):
        raise SpecRefused("the protocol states its sha256 (Q-192's protocol_sha256)")
    margin = _num(nh["margin"], "the no-harm margin")
    if margin < 0 or not isinstance(nh["margin_row"], str) or not (nh["margin_row"] == FIXTURE_ROW or
                                                                 re.fullmatch(r"E-\d+", nh["margin_row"])):
        raise SpecRefused("the no-harm margin is a non-negative number with its decision row E-NNN")
    if ob["rule_id"] != W42_RULE or not isinstance(ob["values_row"], str) or \
            not (ob["values_row"] == FIXTURE_ROW or re.fullmatch(r"E-\d+", ob["values_row"])) or \
            not isinstance(ob["code_sha256"], str) or not _HEX64.fullmatch(ob["code_sha256"]):
        raise SpecRefused(f"the objective is {W42_RULE}'s, named by the row pinning its values file and its code's "
                          "sha256")
    rule = pl["rule"]
    if not isinstance(rule, dict) or rule.get("margin") != DELTA_STAR or rule.get("side") != "worse":
        raise SpecRefused("the plateau rule's margin is the word 'delta_star' (the rule's, never typed) and its side "
                          "'worse' (n-c)")
    for k in PART_NAMES:
        b = parts[k]
        keys = {"id", "params", "data", "sha256"} | ({"keys"} if k == "gate" else set()) | \
            ({"digest"} if k == "space" else set())
        if not isinstance(b, dict) or set(b) != keys or not isinstance(b["params"], dict) or \
                not isinstance(b["data"], dict) or not _HEX64.fullmatch(str(b["sha256"])) or \
                not all(isinstance(v, str) and _HEX64.fullmatch(v) for v in b["data"].values()):
            raise SpecRefused(f"the part {k} is {{{', '.join(sorted(keys))}}} (its data by sha256), got {b!r}")
    if not isinstance(parts["gate"]["keys"], list) or not parts["gate"]["keys"]:
        raise SpecRefused("the gate declares the keys it reads (F-10)")
    if not _HEX64.fullmatch(str(parts["space"]["digest"])):
        raise SpecRefused("the space declares its built digest (M-4)")
    if not isinstance(parts["engine"], dict) or set(parts["engine"]) != {"id", "sha256"}:
        raise SpecRefused("the engine is bound by {id, sha256}")
    out = Spec(raw=s, prereg_id=pid, survey_n=_int(sv["n"], "the survey size"), method=str(sv["method"]),
               survey_seed=_int(sv["seed"], "the survey seed"),
               max_proposals=_int(sv["max_proposals"], "max_proposals"),
               rounds=_int(rd["count"], "the rounds' count"), round_seed=_int(rd["seed"], "the rounds' seed"),
               round_kw={k: rd[k] for k in ROUND_KEYS}, measure=str(pr["measure"]),
               blocks=tuple((str(b[0]), str(b[1])) for b in pr["blocks"]), seeds=seeds,
               horizon=_int(pr["horizon"], "the horizon"), protocol_sha256=pr["sha256"], baselines=BASELINES,
               baseline_seed=_int(bl["seed"], "the baselines' seed"),
               candidates=_int(fi["candidates"], "the candidates' count"), reread_seeds=reread, z=z,
               no_harm_margin=margin, margin_row=nh["margin_row"], values_row=ob["values_row"],
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


def _head_decisions() -> str:
    """The decision log as the checkout's commit holds it (m-1); empty outside git."""
    r = _git("show", "HEAD:DECISIONS.md")
    return r.stdout if r.returncode == 0 else ""


def _row(text: str, row_id: str) -> str | None:
    for line in text.splitlines():
        m = R.ROW.match(line)
        if m and m.group(1) == row_id:
            return line
    return None


def check_pinned(path: Path, sha: str, spec: Spec, *, results_dir: Path, pin_fixture: str | None) -> str:
    """The pin's decision row (`FIXTURE_ROW` under a fixture pin), else `NotPinned`; this repository's log only."""
    if pin_fixture is not None:
        if _inside(path, ROOT / "prereg"):
            raise NotPinned("REFUSED: a fixture pin never stands for a declaration under prereg/ (pin it by its row)")
        if "results" in {x.lower() for x in results_dir.resolve().parts}:
            raise NotPinned("REFUSED: a fixture-pinned survey writes outside any results/ folder")
        if pin_fixture != FIXTURE_PREFIX + sha:
            raise NotPinned(f"REFUSED: the fixture pin does not match the declaration's LF sha256 {sha[:12]}")
        return FIXTURE_ROW
    try:
        rel = path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as e:
        raise NotPinned(f"REFUSED: {path} is not a file of this repository ({ROOT})") from e
    if not SEARCH_DECLARATION.fullmatch(rel) or not rel.startswith(f"prereg/{spec.prereg_id}_"):
        raise NotPinned(f"REFUSED: a search's declaration is prereg/{spec.prereg_id}_<name>.md, not {rel}")
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


def _num_literal(x: float) -> str:
    return json.dumps(x)


VALUES_NAME = "w42_r2_values.csv"                        # W42-R2's OUTPUT_NAME, which the values' row names
_MARGIN_NAME = r"no[-_ ]harm[-_ ]margin"


#: the first numeric token after the margin's name, matched in full (sign, exponent and percent included, so each can
#: be refused)
_NUM_TOKEN = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?%?", re.ASCII)
#: Q-186c: an operator or a unit after the number, after optional whitespace -- the number is not the margin then
_AFTER_OPERATOR = re.compile(r"\s*(?:[/*^\u00d7\-\u2013\u2212:%\u2030]|per\s*cent\b|percent\b|bp\b)",
                             re.IGNORECASE)
#: Q-186c: all that may follow the number -- the end of the line, whitespace then a letter or `(`, or closing
#: punctuation (`` ` ``, `)`, `|`, `;` after optional whitespace; `.` or `,` before whitespace or the end)
_AFTER_ALLOWED = re.compile(r"\s*$|\s+[A-Za-z(]|\s*[`)|;]|[.,](?:\s|$)", re.ASCII)
#: what may stand between the margin's name and its number: spaces, backticks or asterisks, and one `is`, `of`, `at`,
#: `=` or `:`
_MARGIN_GAP = re.compile(r"[\s`*]*(?:(?:is|of|at|=|:)[\s`*]*)?", re.IGNORECASE)


def margin_row_carries(line: str, margin: float) -> bool:
    """Q-186 m-2, Q-186b F-3: the row names the no-harm margin, and the first number after that name (directly, or
    after `is`, `of`, `at`, `=` or `:`) is the margin: a plain ASCII decimal -- no sign, exponent or percent, not run on
    into another number (`0.0.5`, `0.0,05`) or a word, followed by no operator or unit (`/ * ^ x - : % per cent bp`,
    whitespace allowed before them) and by nothing but the end, whitespace then a letter or `(`, or closing
    punctuation -- whose float equals it exactly; and the name occurs once in the row. So 0.0055, 0.0051, 10.005,
    -0.005, 0.005e-3, 0.005 %, 0.005/2, 0.005-0.01, "not 0.005" and "0.01 replaced: ... now 0.005" never stand for
    0.005 (Q-186c)."""
    names = list(re.finditer(_MARGIN_NAME, line, re.IGNORECASE))
    if len(names) != 1:                                     # Q-186c: named twice ("0.01 replaced: ... now 0.005")
        return False
    name = names[0]
    tok = _NUM_TOKEN.search(line, name.end())
    if tok is None or not _MARGIN_GAP.fullmatch(line[name.end():tok.start()]):
        return False
    t = tok.group(0)
    if t[0] in "+-":
        return False
    if t.endswith("%"):
        return False
    if "e" in t.lower():
        return False
    rest = line[tok.end():]                                 # a run-on (0.0.5, 0.0,05, 0.005x) fails _AFTER_ALLOWED
    if _AFTER_OPERATOR.match(rest):
        return False
    if not _AFTER_ALLOWED.match(rest):
        return False
    return float(t) == float(margin)


def values_row_carries(line: str, values_sha: str, values_name: str = VALUES_NAME) -> bool:
    """Q-186 m-2, Q-186b F-3: the row names `W42-R2` (never `W42-R20`), its values file as a whole word (never
    `old_w42_r2_values.csv.bak`) and carries the file's sha256 as a whole 64-hex word."""
    return re.search(re.escape(W42_RULE) + r"(?!\d)", line) is not None and \
        re.search(r"(?<![\w.])" + re.escape(values_name) + r"(?![\w.])", line) is not None and \
        re.search(r"(?<![0-9a-f])" + re.escape(values_sha) + r"(?![0-9a-f])", line) is not None


def check_rows(spec: Spec, pin_row: str, values_sha: str, fixture: bool, values_name: str = VALUES_NAME) -> None:
    """The margin's row and the values' row: each a row of this repository's log before the declaration's pin row, the
    margin's naming the no-harm margin and carrying its number (`margin_row_carries`), the values' naming W42-R2 and
    its file and carrying the file's sha256 (`values_row_carries`). Under a fixture pin a row may be `FIXTURE_ROW`;
    any other row is checked as under a pin."""
    text = _decisions()
    pin_n = None if pin_row == FIXTURE_ROW else int(pin_row[2:])
    for what, rid, carries, must in (
            ("the no-harm margin's", spec.margin_row, lambda ln: margin_row_carries(ln, spec.no_harm_margin),
             f"the no-harm margin {_num_literal(spec.no_harm_margin)}"),
            (f"{W42_RULE}'s values'", spec.values_row, lambda ln: values_row_carries(ln, values_sha, values_name),
             f"{W42_RULE}, {values_name} and sha256 {values_sha}")):
        if rid == FIXTURE_ROW:
            if not fixture:
                raise NotPinned(f"REFUSED: {what} row is a decision row under a pin, not {FIXTURE_ROW!r}")
            continue
        line = _row(text, rid)
        if line is None:
            raise NotPinned(f"REFUSED: {what} row {rid} is not a row of DECISIONS.md")
        if pin_n is not None and int(rid[2:]) >= pin_n:
            raise NotPinned(f"REFUSED: {what} row {rid} does not come before the declaration's pin row {pin_row}")
        if not carries(line):
            raise NotPinned(f"REFUSED: {what} row {rid} does not carry {must!r}")


def check_once(sha: str, results_dir: Path, name: str) -> None:
    """F-5, m-1: no output of this run's names in the folder, no variants row of this declaration, and no finalists'
    token or row naming this run's outputs in the decision log -- as the tree holds it and as its commit does."""
    there = [f"{name}_{o}.csv" for o in OUTPUTS if (results_dir / f"{name}_{o}.csv").exists()]
    if there:
        raise RunRepeated(f"REFUSED: {there} exist in {results_dir}: a result is never overwritten")
    if any(r.get("params", {}).get("_declaration_sha256") == sha for r in _existing_rows(results_dir / "variants.jsonl")):
        raise RunRepeated(f"REFUSED: the variants ledger in {results_dir} already counts a run of this declaration "
                          f"({sha[:12]}): a survey is run once")
    for text in (_decisions(), _head_decisions()):
        if any(t.get("sha") == sha for t in R.heldout_tokens(text, "finalists")):
            raise RunRepeated(f"REFUSED: a finalists' token for this declaration ({sha[:12]}) is in the log")
        hit = [f"{name}_{o}" for o in OUTPUTS if f"{name}_{o}" in text]
        if hit:
            raise RunRepeated(f"REFUSED: the decision log already records this run ({hit[0]}): a survey is run once")


def _once_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except ValueError as e:
            raise RunRepeated(f"REFUSED: the once-record {path} line {i} is not JSON ({e}): it is append-only and "
                              "read whole, so a damaged record refuses every run") from e
        if not isinstance(rec, dict) or not isinstance(rec.get("declaration_sha256"), str):
            raise RunRepeated(f"REFUSED: the once-record {path} line {i} names no declaration_sha256")
        out.append(rec)
    return out


def once_location_problem(path: Path, root: Path | None = None) -> str | None:
    """Q-186 m-5, Q-186c n-3: the once-record lies outside the checkout (by its unresolved and its resolved path), and
    its markers' folder beside it is neither a link nor a git checkout (a clean run of that name), so no
    `run_clean.py --discard` or `--remove` of a checkout can reach either."""
    root = Path(ROOT if root is None else root)
    if _lexically_inside(path, root) or _inside(path, root):
        return f"the once-record {path} lies inside the checkout {root}"
    markers = Path(path).parent / Path(path).stem           # beside the log: only a link or a checkout moves it
    if _is_link(markers):
        return f"the once-markers' folder {markers} is a link (a junction could lead it into a checkout)"
    if os.path.lexists(markers / ".git"):
        return f"the once-markers' folder {markers} is a git checkout (a clean run of that name): --remove would drop it"
    return None


def once_marker(path: Path, sha: str) -> Path:
    """Q-186b F-4: the declaration's exclusive marker beside the log: `<log's folder>/<log's stem>/<sha256>.json`."""
    path = Path(path)
    return path.parent / path.stem / f"{sha}.json"


def check_once_record(sha: str, path: Path) -> None:
    """Q-186 m-5, Q-186b F-4: no earlier run of this declaration (its LF sha256): no marker, and no line in the
    append-only log."""
    marker = once_marker(path, sha)
    if os.path.lexists(marker):
        raise RunRepeated(f"REFUSED: the once-marker {marker} exists: this declaration ({sha[:12]}) has run (a survey is "
                          "run once, from any checkout)")
    seen = [r for r in _once_records(Path(path)) if r["declaration_sha256"] == sha]
    if seen:
        raise RunRepeated(f"REFUSED: the once-record {path} already holds a run of this declaration ({sha[:12]}: run "
                          f"{seen[0].get('run_id')!r}, commit {str(seen[0].get('commit'))[:12]!r}): a survey is run "
                          "once, from any checkout")


def record_once(sha: str, path: Path, record: Mapping[str, Any]) -> str:
    """Q-186 m-5, Q-186b F-4, before the first cell: checked again; the marker created exclusively (`O_CREAT |
    O_EXCL`: of two runs that both passed the check, exactly one creates it, the other refuses); then one line
    appended to the log (never rewritten). Returns the line, which the entry script prints."""
    path = Path(path)
    check_once_record(sha, path)
    marker = once_marker(path, sha)
    marker.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps({**dict(record), "declaration_sha256": sha}, sort_keys=True, default=str)
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0))
    except FileExistsError as e:
        raise RunRepeated(f"REFUSED: another run of this declaration ({sha[:12]}) created the once-marker {marker} "
                          "first: a survey is run once") from e
    with os.fdopen(fd, "wb") as fh:
        fh.write((line + "\n").encode("utf-8"))
        fh.flush()
        os.fsync(fh.fileno())
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return line


FOLDERID_LOCAL_APP_DATA = "F1B32785-6FBA-4FCF-9D55-7B8E7F157091"
_UNSET: Any = object()


def known_local_appdata() -> Path | None:
    """The Windows known folder LocalAppData (`SHGetKnownFolderPath`, through ctypes), None where it cannot be read."""
    if os.name != "nt":
        return None
    import ctypes
    import uuid
    guid = (ctypes.c_byte * 16).from_buffer_copy(uuid.UUID(FOLDERID_LOCAL_APP_DATA).bytes_le)
    out = ctypes.c_wchar_p()
    hr = ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(out))
    try:
        return Path(out.value) if hr == 0 and out.value else None
    finally:
        ctypes.windll.ole32.CoTaskMemFree(out)


def localappdata_problem(env: Mapping[str, str] | None = None, known: Any = _UNSET,
                         runs_dir: Path | None = None) -> str | None:
    """Q-186b F-4, under a pin: the `LOCALAPPDATA` variable (from which `RUNS_DIR`, the clean checkouts and the
    once-record are placed) is the Windows known folder, and `RUNS_DIR` lies in it; else what differs."""
    env = os.environ if env is None else env
    k = known_local_appdata() if known is _UNSET else known
    v = env.get("LOCALAPPDATA")
    runs = Path(RUNS_DIR if runs_dir is None else runs_dir)

    def norm(x: Any) -> str:
        return os.path.normcase(os.path.abspath(x))
    if k is None:
        return "the Windows known folder LocalAppData cannot be read"
    if not v or norm(v) != norm(k):
        return f"LOCALAPPDATA is {v!r}, not the Windows known folder {k}"
    if norm(runs) != norm(Path(k) / "stage2-extended-runs"):
        return f"the runs folder {runs} is not the known folder's {Path(k) / 'stage2-extended-runs'}"
    return None


def lock_problem(start: Path | None = None, env: Mapping[str, str] | None = None) -> str | None:
    """Q-186b F-4, Q-186c, under a pin: `run.lock` at the main repository's root is held, and by this run -- the
    lock's job equal to `S2X_LOCK_HOLDER` and to this clean run's name (`S2X_CLEAN_RUN`), as `run_clean.py --hours
    --mem-gb` sets both to its `--name` (no pid is checked: `set-pid` follows the launch); else what is wrong."""
    from extended import lock_guard as LG
    env = os.environ if env is None else env
    root = LG.main_root(ROOT if start is None else start)
    if root is None:
        return "the main repository's root cannot be found, so run.lock cannot be checked"
    lock = root / LG.LOCK_NAME
    if not lock.exists():
        return f"run.lock is not held at {root}: a pinned survey runs under it (run_clean.py --hours --mem-gb)"
    shown, job = LG._job(lock)
    holder = env.get(LG.LOCK_HOLDER_ENV)
    if job is None or holder != job:
        return f"run.lock is held by {shown}, and this run's {LG.LOCK_HOLDER_ENV} is {holder!r}"
    if env.get(CLEAN_RUN_ENV) != job:                       # Q-186c: run_clean takes the lock under its own --name
        return (f"run.lock is held by {shown}, and this clean run is {env.get(CLEAN_RUN_ENV)!r}: a holder name typed "
                "by hand is not this run's lock")
    return None


# ------------------------------------------------------------------------------------------------ the objective


@dataclass(frozen=True)
class Objective:
    """W42-R2's pinned values as the survey reads them (the module docstring)."""

    values: Mapping[str, Any]
    values_sha256: str
    delta: float
    limits: tuple[Mapping[str, Any], ...]                      # name, direction <= / >=, bound, vacuous
    check_level: float
    floor: float
    fee_unit: float
    guards: Mapping[str, Any]


#: the names the survey reads from W42-R2's module: its tables and its limits (the headroom-corrected values and the
#: floor on the median `net_month_12`, E-296), and the public scoring path it re-exports; every other name the survey
#: reads (the composite's tables, the null journeys, delta*'s constants, the calendars) is W42-R1's, whose code W42-R2
#: runs unchanged (`wave42_r2`'s docstring: "one code path")
W42_R2_NAMES = ("RULE_ID", "OUTPUT_NAME", "APPLY_SCRIPT", "LIMITS", "REQUIRED", "HORIZONS", "CONSTANTS",
                "limit_estimate", "limit_check", "limit_per_seed_sd", "composite_per_seed", "null_composites",
                "do_nothing_floor", "above_floor", "values_from_rows")


class ObjectiveRule(types.ModuleType):
    """W42-R2 as the survey calls it (the module docstring): `W42_R2_NAMES` from `extended.wave42_r2`, every other
    name looked up on `extended.wave42` at call time (so a value set there -- a pinned calendar sha -- is the one read).
    Its `__file__` is W42-R2's module, whose raw sha256 the values' sidecar records."""

    def __init__(self, r2: Any, r1: Any) -> None:
        super().__init__("extended.survey.objective_rule", "W42-R2 over W42-R1's code (E-296, E-299)")
        self.__file__ = r2.__file__
        self._r2, self._r1 = r2, r1
        for n in W42_R2_NAMES:
            setattr(self, n, getattr(r2, n))

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__") or name in ("_r1", "_r2") or name in W42_R2_NAMES:
            raise AttributeError(f"{name}: a W42-R2 name never falls back to W42-R1's" if name in W42_R2_NAMES
                                 else name)
        return getattr(self._r1, name)


_RULE: list[Any] = []


def _wave42() -> Any:
    """The objective's rule, W42-R2 (`ObjectiveRule`), one object a process."""
    if not _RULE:
        from extended import wave42, wave42_r2
        if wave42_r2.PARENT_RULE_ID != wave42.RULE_ID or wave42_r2.RULE_ID != W42_RULE:
            raise PartRefused(f"REFUSED: extended.wave42_r2 is not {W42_RULE} over {wave42.RULE_ID}")
        _RULE.append(ObjectiveRule(wave42_r2, wave42))
    return _RULE[0]


def read_values(path: Path, W: Any | None = None) -> dict[str, Any]:
    """W42-R2's output, `key` / `value_json` rows (W42-R1's section 9.1 row schema, which W42-R2 keeps), into its
    values dict by the rule's own `values_from_rows`."""
    import csv as _csv
    import io

    W = W or _wave42()
    rows = list(_csv.DictReader(io.StringIO(path.read_bytes().decode("utf-8"))))
    if not rows or set(rows[0]) != {"key", "value_json"}:
        raise SpecRefused(f"REFUSED: {path.name} is not {W42_RULE}'s output: its columns are key and value_json")
    try:
        return W.values_from_rows(rows)
    except ValueError as e:
        raise SpecRefused(f"REFUSED: {path.name}: {e}") from e


def _sidecar(side: Path) -> dict[str, Any]:
    """A sidecar manifest as a JSON object, or `SpecRefused` (Q-186 n-5: a malformed sidecar refuses as the spec's)."""
    try:
        man = json.loads(side.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise SpecRefused(f"REFUSED: the sidecar {side.name} is not JSON: {e}") from e
    if not isinstance(man, dict):
        raise SpecRefused(f"REFUSED: the sidecar {side.name} is not a JSON object")
    return man


def _w42_apply() -> Any:
    """W42-R2's application script, loaded by its path in this checkout, for its own `commit_problem` (m-3)."""
    p = ROOT / W42_SCRIPT
    if not p.is_file():
        raise PartRefused(f"REFUSED: {W42_SCRIPT} is not in this checkout: the values' provenance is checked by its "
                          "own commit rule")
    spec = importlib.util.spec_from_file_location("_survey_wave42_r2_apply", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _verify_result(p: Path) -> tuple[bool, str]:
    """`extended.results.verify_result` (it puts the vendored tree on sys.path: a pinned survey's own process)."""
    from extended.results import verify_result
    try:
        return verify_result(p)
    except Exception as e:                                   # a manifest off the vendored form fails closed
        return False, f"{type(e).__name__}: {e}"


_SHA40 = re.compile(r"[0-9a-f]{40}")
W42_PIN_FILE = "config/w42_r2_pin.json"                 # wave42_r2_apply.PIN_FILE: the checkout's W42-R2 pin


def _git_in(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def head_pinned_commit(repo: Path) -> str | None:
    """Q-186c n-1: W42-R2's pinned commit as the run's commit holds it (`git show HEAD:config/w42_r2_pin.json`, never
    the working tree, which `--skip-worktree` could hide from `git status`); None when HEAD has no pin file;
    `SpecRefused` when it is malformed (not JSON, not an object, its `commit` not 40 hex)."""
    r = _git_in(Path(repo), "show", f"HEAD:{W42_PIN_FILE}")
    if r.returncode:
        return None
    try:
        got = json.loads(r.stdout)
    except ValueError as e:
        raise SpecRefused(f"REFUSED: HEAD's {W42_PIN_FILE} is not JSON: {e}") from e
    c = got.get("commit") if isinstance(got, dict) else None
    if not (isinstance(c, str) and _SHA40.fullmatch(c)):
        raise SpecRefused(f"REFUSED: HEAD's {W42_PIN_FILE} names no commit (40 hex): {r.stdout[:120]!r}")
    return c


def values_provenance_problems(man: Mapping[str, Any], csv_path: Path, *, repo: Path | None = None,
                               apply: Any = None, verify: Callable[[Path], tuple[bool, str]] | None = None
                               ) -> list[str]:
    """Q-186 m-3, Q-186b F-2, under a pin: W42-R2's values file is a pinned application -- `parameters.pinned_commit`
    40 hex and equal to the run's commit's pin (`head_pinned_commit`: HEAD's `config/w42_r2_pin.json`); the
    manifest's `git_commit` 40 hex and clean (no `-dirty`), a commit of this repository (`git cat-file -e`) and an
    ancestor of the run's HEAD (`git merge-base --is-ancestor`); `wave42_r2_apply.commit_problem(repo, pinned_commit,
    head=git_commit)` None (the pinned commit itself, or a descendant touching none of W42-R2's imported files, W42-R1's
    among them: the rule's own test) -- and `extended.results.verify_result` passes. Empty when all hold."""
    params = man.get("parameters") if isinstance(man.get("parameters"), Mapping) else {}
    pin, head = params.get("pinned_commit"), man.get("git_commit")
    out = []
    if not (isinstance(pin, str) and _SHA40.fullmatch(pin)):
        out.append(f"its parameters.pinned_commit is {pin!r}, not 40 hex: not a pinned application")
    if not isinstance(head, str) or not _SHA40.fullmatch(head.removesuffix("-dirty")):
        out.append(f"its git_commit is {head!r}, not 40 hex")
    elif head.endswith("-dirty"):
        out.append(f"its git_commit {head!r} is -dirty: written from an uncommitted tree")
    if not out:
        repo_ = Path(ROOT if repo is None else repo)
        A = apply or _w42_apply()
        mine = head_pinned_commit(repo_)
        if pin != mine:
            out.append(f"its pinned_commit {str(pin)[:12]} is not this checkout's pin ({W42_PIN_FILE}: {mine!r})")
        elif _git_in(repo_, "cat-file", "-e", f"{head}^{{commit}}").returncode:
            out.append(f"its git_commit {str(head)[:12]} is no commit of this repository")
        elif _git_in(repo_, "merge-base", "--is-ancestor", head, "HEAD").returncode:
            out.append(f"its git_commit {str(head)[:12]} is not an ancestor of this run's HEAD")
        else:
            why = A.commit_problem(repo_, pin, head=head)
            if why is not None:
                out.append(f"{W42_RULE}'s commit rule refuses it: {why}")
    ok, msg = (verify or _verify_result)(Path(csv_path))
    if not ok:
        out.append(f"verify_result: {msg}")
    return out


def load_objective(W: Any) -> Objective:
    """W42-R2's result file by name, its sidecar checked (C-1), its public functions required, its floor self-checked,
    every limit set (m-2)."""
    missing = [n for n in W42_PUBLIC if not callable(getattr(W, n, None))]
    eps = getattr(W, "DO_NOTHING_EPS", None)
    if isinstance(eps, bool) or not isinstance(eps, (int, float)) or not (math.isfinite(eps) and eps > 0):
        missing.append("DO_NOTHING_EPS")
    if missing:
        raise PartRefused(f"REFUSED: {W42_RULE}'s public functions {missing} are not on this commit (the survey calls the "
                          "rule's own code, never a copy of it)")
    p = ROOT / "results" / W.OUTPUT_NAME
    side = Path(f"{p}.manifest.json")
    if not p.is_file() or not side.is_file():
        raise SpecRefused(f"REFUSED: {W42_RULE}'s output {p.name} and its sidecar are both required")
    man = _sidecar(side)
    params = man.get("parameters") or {}
    if not isinstance(params, dict):
        raise SpecRefused(f"REFUSED: {W42_RULE}'s sidecar {side.name}: its parameters are not a JSON object")
    values = read_values(p, W)
    rule_sha = _raw_sha(inspect.getsourcefile(W))
    for what, got, want in (("its file's sha256", man.get("sha256"), _raw_sha(p)),
                            ("its script", man.get("script"), W42_SCRIPT),
                            ("its rule id", params.get("rule_id"), W42_RULE),
                            ("the rule module's sha256 (raw bytes)", params.get("rule_module_sha256"), rule_sha),
                            ("its values' digest", params.get("values_sha256"), W.Wave42Values(values).digest())):
        if got != want:
            raise SpecRefused(f"REFUSED: {W42_RULE}'s output: {what} is {str(got)[:16]!r}, not {str(want)[:16]!r}")
    if values.get("rule_id") != W42_RULE or W.RULE_ID != W42_RULE:
        raise SpecRefused(f"REFUSED: the values are not {W42_RULE}'s")
    try:
        names = {lim.name for lim in W.LIMITS}
        lims = {x["name"]: x for x in values["limits"]["values"]}
        unset = sorted(n for n in names if n not in lims or lims[n].get("status") != "set")
        if unset:
            raise SpecRefused(f"REFUSED: {W42_RULE}'s limits {unset} are not set: a limit is never dropped (m-2)")
        limits = tuple({"name": n, "direction": "<=" if lims[n]["direction"] == "ceiling" else ">=",
                        "bound": float(lims[n]["value"]), "vacuous": bool(lims[n].get("vacuous")),
                        "vacuous_reason": lims[n].get("vacuous_reason")}
                       for n in [lim.name for lim in W.LIMITS])
        nj = values["null_journeys"]
        if nj["floor"]["name"] != DO_NOTHING:
            raise SpecRefused(f"REFUSED: {W42_RULE}'s floor is not the do-nothing journey's")
        ob = Objective(values, W.Wave42Values(values).digest(), float(values["delta_star"]["value"]), limits,
                       float(values["limits"]["check_level"]), float(nj["floor"]["value"]),
                       float(values["budgets"]["fee_unit"]), dict(values.get("inactivity_guards", {})))
    except (KeyError, TypeError, ValueError) as e:
        raise SpecRefused(f"REFUSED: {W42_RULE}'s values lack {e}") from e
    if not ob.delta > 0:
        raise SpecRefused(f"REFUSED: {W42_RULE}'s delta* is above zero")
    horizon = max(W.HORIZONS)
    arm = {k: np.asarray([[float(x)]]) for k, x in W.null_journeys(ob.fee_unit)[DO_NOTHING].items()}
    for k in W.REQUIRED:
        arm.setdefault(k, np.zeros((1, 1)))
    got = float(np.asarray(W.composite_per_seed(values, [horizon], arm)).ravel()[0])
    rule = float(W.do_nothing_floor(values, ob.fee_unit))
    if abs(got - ob.floor) > FLOOR_SELF_CHECK or abs(rule - ob.floor) > FLOOR_SELF_CHECK:
        raise SpecRefused(f"REFUSED: the public composite of the do-nothing journey is {got!r} (the rule's own "
                          f"do_nothing_floor {rule!r}), the values' floor {ob.floor!r}: the composite is not the "
                          "one the values were set with (C-1)")
    return ob


def load_calendar(W: Any, values: Mapping[str, Any]) -> Any:
    """The pinned search calendar (Q-197), through its loader, by `wave42.SEARCH_CALENDAR_SHA256` (W42-R1's constant,
    which W42-R2 reads), its dates the ones W42-R2 was set on (M-3)."""
    try:
        loader = importlib.import_module("extended.search_calendar").load_search_calendar
    except (ImportError, AttributeError) as e:
        raise PartRefused(f"REFUSED: the search calendar's loader (Q-197) is not on this commit: {e}") from e
    if W.SEARCH_CALENDAR_SHA256 is None:
        raise PartRefused("REFUSED: wave42.SEARCH_CALENDAR_SHA256 is not pinned yet (Q-197's result)")
    cal = loader(ROOT / "results" / W.SEARCH_CALENDAR)
    if cal.file_sha256 != W.SEARCH_CALENDAR_SHA256:
        raise SpecRefused(f"REFUSED: {W.SEARCH_CALENDAR}'s sha256 is not the pinned one")
    dates = tuple(str(d) for d in cal.dates)
    if W.calendar_digest(dates) != values["h4"]["calendar_sha256"]:
        raise SpecRefused(f"REFUSED: the search calendar is not the one {W42_RULE}'s values were set on")
    if not dates or dates[-1] != SEARCH_LAST:
        raise SpecRefused(f"REFUSED: the search calendar ends on {SEARCH_LAST}")
    if [int(cal.sessions_left(d)) for d in dates[:1] + dates[-1:]] != [len(dates), 1]:
        raise SpecRefused("REFUSED: the calendar's sessions left are not the rule's (len - position, the start "
                          "counted)")
    return cal


def composite(ctx: "Context", arm: Mapping[str, Any], sl: Sequence[int]) -> np.ndarray:
    """The rule's composite per seed (higher better), by its own public function (W42-R1's, which W42-R2 keeps)."""
    return np.asarray(ctx.W.composite_per_seed(ctx.obj.values, list(sl), arm), float).ravel()


def limit_value(ctx: "Context", arm: Mapping[str, Any], sl: Sequence[int], lim: Mapping[str, Any]
                ) -> tuple[float, np.ndarray]:
    """A limit's point estimate (W42-R2's `limit_estimate`: its declared statistic over its complete starts, pooled
    over seeds) and the same estimate seed by seed (each seed's column)."""
    W, v, name = ctx.W, ctx.obj.values, lim["name"]
    point = float(W.limit_estimate(v, list(sl), arm, name))
    J = np.asarray(next(iter(arm.values()))).shape[1]
    per = np.array([float(W.limit_estimate(v, list(sl), {k: np.asarray(x)[:, c:c + 1] for k, x in arm.items()}, name))
                    for c in range(J)])
    return point, per


def t_threshold(z: float, n: int) -> float:
    """The declared z read as its one-sided level, then the t quantile at n - 1 degrees of freedom (F-7)."""
    from scipy import stats
    return float(stats.t.ppf(stats.norm.cdf(z), n - 1))


# ------------------------------------------------------------------------------------------------ the context


@dataclass
class Context:
    spec: Spec
    E: Engine
    W: Any
    obj: Objective
    calendar: tuple[str, ...]
    cal: Any
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
    fixture: bool = False
    rows: list[dict[str, Any]] = field(default_factory=list)
    readings: list[Any] = field(default_factory=list)
    limit_readings: dict[str, list[Any]] = field(default_factory=dict)
    selection: dict[str, dict[str, Any]] = field(default_factory=dict)
    rounds: list[Any] = field(default_factory=list)
    records: list[dict[str, Any]] = field(default_factory=list)
    floored: list[dict[str, Any]] = field(default_factory=list)
    memo: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = field(default_factory=dict)
    _pos: dict[str, int] = field(default_factory=dict)

    @property
    def limit_names(self) -> tuple[str, ...]:
        return tuple(lim["name"] for lim in self.obj.limits)


def new_ledger(E: Engine) -> Any:
    """The run's one cell ledger: the engine's own, whose survey role declares the protocol."""
    return E.SS.CellLedger()


def _held_out_first(ctx: Context, out: RunOutput) -> None:
    """F-4: a held-out tag, block, horizon or start refuses the whole run, before anything else is read of it."""
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
    late = [d for d in out.starts if str(d) > SEARCH_LAST]
    if late:
        raise SS.HeldOutInput(f"REFUSED: the runner reports a start on {late[0]}, after the search years")


def sessions_left(ctx: Context, starts: Sequence[str]) -> np.ndarray:
    """M-3: each start on the pinned search calendar and inside a protocol block, strictly increasing; its sessions
    left on W42-R1's definition (`len(calendar) - position`, the start session counted), computed here."""
    if not ctx._pos:
        ctx._pos.update({d: i for i, d in enumerate(ctx.calendar)})
    s = [str(d) for d in starts]
    if not s or s != sorted(set(s)):
        raise SurveyRefused("the runner's starts are strictly increasing dates")
    off = [d for d in s if d not in ctx._pos]
    if off:
        raise SurveyRefused(f"the runner's start {off[0]} is not a session of the pinned search calendar (M-3)")
    out = [d for d in s if not any(b0 <= d <= b1 for b0, b1 in ctx.protocol.blocks)]
    if out:
        raise SurveyRefused(f"the runner's start {out[0]} lies outside the protocol's blocks")
    return np.array([int(ctx.cal.sessions_left(d)) for d in s])                    # Q-197's own definition


def _check_real_path(out: RunOutput, keys: set[str]) -> None:
    if set(out.real_path) != {AS_TRADED, REFLECTED} or any(not keys <= set(v) for v in out.real_path.values()):
        raise SurveyRefused(f"the runner reports exactly the real path's {AS_TRADED} and {REFLECTED} readings, each on "
                            f"every key {W42_RULE} reads; got {sorted(out.real_path)}")


def validate_values(ctx: Context, name: str, arm: Mapping[str, Any], sl: np.ndarray) -> None:
    """m-3: as the rule checks the baselines': each key finite and inside `REQUIRED`'s range on its complete starts, and
    no unit paid before its first pass. A NaN refuses under its own label."""
    W = ctx.W
    for key, (h, lo, hi) in W.REQUIRED.items():
        x = np.asarray(arm[key], float)
        rows = sl >= h
        if not rows.any():
            raise SurveyRefused(f"no start of the run has {h} sessions left (E_{h} is empty for {key!r})")
        xe = x[rows]
        if not np.isfinite(xe).all():
            raise SurveyRefused(f"the runner's {name} {key!r} is not finite (a NaN or an infinity) on E_{h} (m-3)")
        if (xe < lo).any() or (xe > hi).any():
            raise SurveyRefused(f"the runner's {name} {key!r} lies outside {W42_RULE}'s range [{lo}, {hi}] (m-3)")
    rW = sl >= W.W
    payout, first = np.asarray(arm["first_payout_days"], float)[rW], np.asarray(arm["first_pass_days"], float)[rW]
    paid = payout <= W.W
    if (first[paid] > payout[paid]).any():
        raise SurveyRefused(f"the runner's {name} has a unit paid before its first pass (m-3)")


def _check_output(ctx: Context, out: Any, protocol: Any) -> np.ndarray:
    """The run's report: held-out first (F-4); then on the protocol given, its starts on the calendar (sessions left
    computed here), every arm and key, paired, one column a seed, the data it read declared, every value valid.
    Returns the sessions left."""
    if type(out) is not RunOutput:
        raise SurveyRefused(f"the runner reports a RunOutput, got {type(out).__name__}")
    _held_out_first(ctx, out)
    if tuple(out.seeds) != tuple(protocol.seeds) or tuple(tuple(b) for b in out.blocks) != tuple(protocol.blocks) \
            or out.horizon != protocol.horizon:
        raise SurveyRefused("the runner ran off the protocol it was given (seeds, blocks or horizon)")
    sl = sessions_left(ctx, out.starts)
    need = set(ctx.W.REQUIRED)
    missing = [a for a in (DESIGN_ARM,) + ctx.spec.baselines if a not in out.arms or not need <= set(out.arms[a])]
    if missing or not set(ctx.gate_keys) <= set(out.arms.get(DESIGN_ARM, {})):
        raise SurveyRefused(f"the runner reports the design's and every baseline's arm on every key {W42_RULE} reads "
                            f"and the gate's keys; incomplete: {missing or 'the gate keys'}")
    _check_real_path(out, need)
    shapes = {np.asarray(x).shape for arm in list(out.arms.values()) + list(out.real_path.values())
              for x in arm.values()}
    if shapes != {(len(sl), len(protocol.seeds))}:
        raise SurveyRefused(f"every arm on the same {len(sl)} starts and one column a seed (paired), got "
                            f"{sorted(shapes)}")
    declared, got = dict(ctx.spec.parts["runner"]["data"]), dict(out.data)
    if got != declared:                                     # Q-186 M-1: equal key for key, both ways
        extra = sorted(k for k in got if k not in declared or declared[k] != got[k])
        missing = sorted(k for k in declared if k not in got)
        raise SurveyRefused(f"the runner's data report is not the declared data (M-4, Q-186 M-1): it read data the "
                            f"declaration does not bind {extra[:3]}; it did not report declared data {missing[:3]}")
    if not isinstance(out.positions, Mapping):
        raise SurveyRefused("the positions are reported per (start, seed) path (n-a)")
    for name, arm in [(a, out.arms[a]) for a in (DESIGN_ARM,) + ctx.spec.baselines] + \
            [(f"real path {k}", v) for k, v in out.real_path.items()]:
        validate_values(ctx, name, arm, sl)
    return sl


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


def _row_of(ctx: Context, role: str, design: Mapping[str, Any], measure: str, r: Any, refused: str = "") -> None:
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
                _row_of(ctx, f"{role}:{BASELINE_ROLE}", {"baseline": b}, ctx.spec.measure, rb)
        elif k not in ("out", "sl"):
            _row_of(ctx, role, design, k, r)


def read_design(ctx: Context, design: Mapping[str, Any], protocol: Any, role: str) -> dict[str, Any]:
    """Steps 3-5 (the module docstring): {measure: Reading} for the design and each limit, `BASELINE_ROLE`:
    {baseline: Reading}, `"out"`: the run, `"sl"`: its sessions left; `_Refused` when the book or the gate refuses."""
    reread = tuple(protocol.seeds) != tuple(ctx.protocol.seeds)
    key = (ctx.E.SS.design_id(design), tuple(protocol.seeds))
    if key in ctx.memo:
        got = ctx.memo[key]
        _rows_of(ctx, f"{role}(memo)", design, got)                        # n-d: every read reported
        return got
    out = ctx.runner(ctx.build_schedule(dict(design)), protocol)
    sl = _check_output(ctx, out, protocol)
    try:
        screen(ctx, out)
    except _Refused as g:
        _row_of(ctx, role, design, "", None, f"{g.cls}: {g.reason}")
        raise
    m, roles = ctx.spec.measure, _roles(ctx, role)
    got: dict[str, Any] = {m: _reading(ctx, design, -composite(ctx, out.arms[DESIGN_ARM], sl), None, out, m, reread,
                                       roles)}
    for lim in ctx.obj.limits:                                  # every read: a neighbour may later be a candidate
        v, per = limit_value(ctx, out.arms[DESIGN_ARM], sl, lim)
        got[lim["name"]] = _reading(ctx, design, per, v, out, lim["name"], reread, roles)
    got[BASELINE_ROLE] = {b: _reading(ctx, {"baseline": b}, -composite(ctx, out.arms[b], sl), None, out, m, reread,
                                      lambda r: r == BASELINE_ROLE) for b in ctx.spec.baselines}
    got["out"], got["sl"] = out, sl
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
    """Step 2: the space-filling survey, every cell counted under ``survey``, whose `begin` checks the protocol, the
    re-read seeds and the limit measures against the declaration's protocol sha256 (Q-192)."""
    s = ctx.spec
    return ctx.E.SS.Sampler(ctx.space, seed=s.survey_seed, method=s.method).survey(
        s.survey_n, ledger=ctx.ledger, protocol=ctx.protocol, reread_seeds=s.reread_seeds,
        measures=ctx.limit_names, declaration_sha256=s.protocol_sha256, max_proposals=s.max_proposals)


def check_engine_rereads(ctx: Context) -> None:
    """Q-192b: the engine reads the declared limit measures on the re-read seeds (F-3), or the run refuses here, after
    the survey's cells and before any read."""
    for name in ctx.limit_names:
        try:
            ctx.ledger.protocol_for(name, reread=True)
        except ctx.E.SS.OffProtocol as e:
            raise PartRefused(f"REFUSED: the engine does not read the limit {name!r} on the re-read seeds (Q-192b; "
                              f"F-3): {e}") from e


def record_baselines(ctx: Context) -> None:
    """The baselines as cells of their own role, recorded through the role's pen and closed (Q-192)."""
    pen = ctx.ledger.begin(BASELINE_ROLE, ctx.spec.baseline_seed)
    for b in ctx.spec.baselines:
        pen.record(ctx.space, {"baseline": b}, refusal=None)
    pen.close()


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
    """F-3, E-230: each limit's **re-read** point estimate inside its bound decides; beside it, never deciding, the
    selection reading, W42-R2's vacuous flag and the one-sided check of crossing -- W42-R2's own `limit_check` (normal
    z_(1 - level) at the values' `check_level`, B-10's form; Q-186 n-1) on the re-read run, whose estimate and inside
    verdict must equal the survey's exactly."""
    out, ok = {}, True
    arm, sl = reread["out"].arms[DESIGN_ARM], reread["sl"]
    for lim in ctx.obj.limits:
        r, s = reread[lim["name"]], selection.get(lim["name"])
        v, b = float(r.value), float(lim["bound"])
        inside = v <= b if lim["direction"] == "<=" else v >= b
        chk = ctx.W.limit_check(ctx.obj.values, list(sl), arm, lim["name"], b, ctx.obj.check_level)
        if float(chk["estimate"]) != v or bool(chk["inside"]) != inside:
            raise LimitDisagrees(f"{W42_RULE}'s limit_check reads {lim['name']} as {chk['estimate']!r} (inside "
                                f"{chk['inside']}), the survey {v!r} (inside {inside}): not one limit")
        out[lim["name"]] = {"value": v, "bound": b, "direction": lim["direction"], "inside": inside,
                            "selection_value": None if s is None else float(s.value),
                            "check_beyond": float(chk["beyond"]), "check_se": float(chk["se"]),
                            "check_z": float(chk["check_z"]), "check_level": float(chk["level"]),
                            "crossing_shown": bool(chk["crossed_at_level"]),
                            "vacuous": lim["vacuous"], "vacuous_reason": lim["vacuous_reason"]}
        ok = ok and inside
    return ok, {"limits": out}


def no_harm(ctx: Context, out: RunOutput, sl: np.ndarray) -> tuple[bool, dict[str, Any]]:
    """O-4's floor: the trigger's own sides, and the as-traded composite no worse than the coin-side as-walked
    (`REFLECTED`) composite by more than the declaration's no-harm margin (point estimates, CHARTER 3.8 (c))."""
    d = float(np.mean(composite(ctx, out.real_path[AS_TRADED], sl) - composite(ctx, out.real_path[REFLECTED], sl)))
    held = out.side_source == TRIGGER and d >= -ctx.spec.no_harm_margin
    return held, {"no_harm": {"side_source": out.side_source, "as_traded_minus_reflected": d,
                              "margin": ctx.spec.no_harm_margin, "margin_row": ctx.spec.margin_row,
                              "held": bool(held)}}


def do_nothing_floor(ctx: Context, r: Any) -> tuple[bool, dict[str, Any]]:
    """V-4, M-2, Q-186 m-1: the composite (the reading's value negated: the float mean over seeds, negation exact)
    above W42-R1's do-nothing floor by more than `DO_NOTHING_EPS`, decided by W42-R1's own `above_floor` -- the one
    comparator of the screen and the held-out verdict, never passed by rounding (1e-9 is far above one ulp)."""
    c = -float(r.value)
    ok = bool(ctx.W.above_floor(c, ctx.obj.floor))
    return ok, {"do_nothing": {"composite": c, "floor": ctx.obj.floor, "eps": float(ctx.W.DO_NOTHING_EPS),
                               "held": ok}}


def not_paid_floor(ctx: Context, got: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    """V-4: the `not_paid_within_B` limit's point estimate inside its bound (W42-R1 always sets it: m-2)."""
    lim = next(x for x in ctx.obj.limits if x["name"] == NOT_PAID)
    v = float(got[NOT_PAID].value)
    ok = v <= lim["bound"] if lim["direction"] == "<=" else v >= lim["bound"]
    return ok, {"not_paid": {"value": v, "bound": lim["bound"], "vacuous": lim["vacuous"], "held": bool(ok)}}


def passes_floors(ctx: Context, got: Mapping[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    """V-4's floors, in their order -- the no-harm floor, the `not_paid_within_B` limit, the do-nothing floor: (passes,
    the first floor failed, every floor's reading)."""
    info: dict[str, Any] = {}
    first = ""
    for name, (ok, part) in (("the no-harm floor", no_harm(ctx, got["out"], got["sl"])),
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


def plateau_step(ctx: Context, finalist: Any) -> Any:
    """`plateau.check` on the ledger's re-read seeds, its margin delta*; a neighbour refused by the book or the gate
    refuses the candidate (raised as `_Refused`)."""
    PL = ctx.E.PL
    rule = PL.PlateauRule(**dict(ctx.spec.plateau_rule, margin=ctx.obj.delta))

    def evaluate(design: Mapping[str, Any], *, protocol: Any) -> Any:
        return read_design(ctx, design, protocol, "plateau")[protocol.measure]      # the composite or a limit

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
                 ("the no-harm floor", no_harm(ctx, got["out"], got["sl"])),
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
        if v.protocol_sha256 != ctx.spec.protocol_sha256:
            raise SurveyRefused("the plateau's verdict is on another protocol than the declaration's (rb2-a)")
        off = [m for m, x in v.reread_limits.items() if abs(x["value"] - float(got[m].value)) > 0.0]
        if off or set(v.reread_limits) != set(ctx.limit_names):
            raise SurveyRefused(f"the plateau's re-read limits are not the survey's ({off or 'another set'})")
        rec.update(plateau={"accepted": bool(v.accepted), "reason": v.reason, "rule": v.rule,
                            "evaluated": v.evaluated, "held": v.held, "protocol_sha256": v.protocol_sha256,
                            "reread_limits": v.reread_limits, "size_at": v.size_at, "size_bound": v.size_bound,
                            "size_label": v.size_label}, kept=bool(v.accepted), reason=v.reason)
        if v.accepted:
            finalists.append(rec)
    return finalists


# ------------------------------------------------------------------------------------------------ the emission


def heldout_problems(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Each variants row naming the held-out years (a date from 2024-01-02 in its params or label) or a held-out tag
    in its label or prereg id -- tags and dates, never substrings of design keys, never the row's timestamp (n-4,
    n-5)."""
    out = []
    for i, row in enumerate(rows):
        tags = " ".join(str(row.get(k, "")) for k in ("label", "prereg_id"))
        scanned = json.dumps({"params": row.get("params", {}), "label": row.get("label", "")}, sort_keys=True,
                             default=str)
        late = [d for d in _ISO.findall(scanned) if d >= str(R.JUDGED_START)]
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
    """The ledger's rows (each carrying the engine's protocol and its sha256), with the declaration's sha256 added,
    checked held-out free."""
    rows = [dict(r, params=dict(r["params"], _declaration_sha256=ctx.sha))
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
    guards = {"inactivity_guards": ctx.obj.guards,
              "vacuous_limits": {lim["name"]: lim["vacuous_reason"] for lim in ctx.obj.limits if lim["vacuous"]}}
    rows = [{"rank": r["rank"], "id": r["id"], "kept": bool(r.get("kept", False)), "reason": r.get("reason", ""),
             "selection_value": r["selection_value"], "reread_value": r.get("reread_value"),
             "design": json.dumps(r["design"], sort_keys=True, default=str),
             "detail": json.dumps({**{k: r[k] for k in ("gaps", "limits", "no_harm", "do_nothing", "plateau")
                                      if k in r}, **guards}, sort_keys=True, default=str)} for r in ctx.records]
    rows += [{"rank": 0, "id": r["id"], "kept": False, "reason": r["reason"], "selection_value": r["selection_value"],
              "reread_value": None, "design": json.dumps(r["design"], sort_keys=True, default=str),
              "detail": json.dumps({**{k: r[k] for k in ("no_harm", "not_paid", "do_nothing") if k in r}, **guards},
                                   sort_keys=True, default=str)} for r in ctx.floored]
    return pd.DataFrame(rows, columns=cols)


def finalists_token(prereg_id: str, sha: str, list_sha: str, *, fixture: bool) -> str:
    """The finalists' token: Q-158's form (`heldout-finalists: F-NN @ <sha> list <sha>`, which `reader` rule 1 reads)
    under a pin only; under a fixture pin a visibly distinct form that no held-out rule reads (Q-186 m-6)."""
    if fixture:
        return f"{FIXTURE_TOKEN} {prereg_id} @ {sha} list {list_sha} (a fixture run: it authorises no held-out read)"
    return f"{REAL_TOKEN} {prereg_id} @ {sha} list {list_sha}"


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
                     "candidate of the finalist order rule, kept or refused and why; the floored cells as rank 0; "
                     f"{W42_RULE}'s inactivity guards and vacuous limits beside", **common)
    out = []
    for i, f in enumerate(finalists, 1):
        text = str(ctx.playbook(dict(f["design"]))).replace("\r\n", "\n")
        out.append({"order": i, "id": f["id"], "design": json.dumps(f["design"], sort_keys=True, default=str),
                    "selection_value": f["selection_value"], "reread_value": f["reread_value"],
                    "gaps": json.dumps(f["gaps"], sort_keys=True), "limits": json.dumps(f["limits"], sort_keys=True),
                    "no_harm": json.dumps(f["no_harm"], sort_keys=True),
                    "do_nothing": json.dumps(f["do_nothing"], sort_keys=True), "plateau_rule": f["plateau"]["rule"],
                    "plateau_reason": f["plateau"]["reason"], "playbook": text,
                    "playbook_sha256": hashlib.sha256(text.encode()).hexdigest(), "fit_sha256": json.dumps(fits)})
    cols = ["order", "id", "design", "selection_value", "reread_value", "gaps", "limits", "no_harm", "do_nothing",
            "plateau_rule", "plateau_reason", "playbook", "playbook_sha256", "fit_sha256"]
    lpath, _ = write(pd.DataFrame(out, columns=cols), f"{name}_finalists",
                     description=f"{ctx.spec.prereg_id}: the finalists' list in the declared order (the finalist "
                     "order rule; empty when none)", **common)
    lsha = _lf_sha(lpath)
    vpath = vwrite(rows, results_dir)                       # last: no counted rows without their results
    token = finalists_token(ctx.spec.prereg_id, ctx.sha, lsha, fixture=ctx.fixture) if out else None
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
    once_line: str | None = None                            # Q-186b F-4: printed by the entry script


def run_survey(declaration: Path | str, *, results_dir: Path | str, name: str, pin_fixture: str | None = None,
               engine: Engine | None = None, writer: Callable[..., Any] | None = None,
               variants_writer: Callable[..., Path] | None = None, once_file: Path | str | None = None) -> Outcome:
    """The whole loop (the module docstring): refusals first, then steps 2-8. `engine`, the writers and `once_file`
    are honoured only under a fixture pin (and the engine is still bound); under a pin the once-record is `ONCE_FILE`,
    outside the checkout."""
    path, out_dir = Path(declaration), Path(results_dir)
    if not path.is_file():
        raise NotPinned(f"REFUSED: the declaration {path} does not exist")
    raw = path.read_bytes()                                                # read once: hashed and parsed (n-3)
    sha = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()
    spec = load_spec(raw)
    pin_row = check_pinned(path, sha, spec, results_dir=out_dir, pin_fixture=pin_fixture)
    fixture = pin_fixture is not None
    own = [k for k in PART_NAMES if str(spec.parts[k]["id"]).startswith("extended.")]
    if fixture and own:
        raise PartRefused(f"REFUSED: a fixture pin builds no extended. part ({own}; Q-186b F-5): a preview of a real "
                          "search on real parts would be counted nowhere -- pin the declaration and run it once")
    if not fixture and any(x is not None for x in (engine, writer, variants_writer, once_file)):
        raise PartRefused("REFUSED: under a pin the engine, the writers and the once-record are this repository's "
                          "own; an injected one is honoured only under a fixture pin")
    E = engine or Engine.default()
    E.check()
    bound = check_bindings(spec, E)
    process = {"commit": FIXTURE_ROW, "entry_sha256": FIXTURE_ROW}
    if not fixture:
        mods = [spec.parts[k]["id"].partition(":")[0] for k in PART_NAMES] + \
            [m.__name__ for m in E.modules().values()] + list(OBJECTIVE_MODULES) + [DRIVER_MODULE]
        process = check_process(out_dir, mods, path)
    once = Path(ONCE_FILE) if not fixture else (Path(once_file) if once_file is not None else None)
    if once is not None:
        where = once_location_problem(once)
        if where:
            raise PartRefused(f"REFUSED: {where} (Q-186 m-5)")
        check_once_record(sha, once)
    check_data(spec)
    W = _wave42()
    obj = load_objective(W)
    values_path = ROOT / "results" / W.OUTPUT_NAME
    if not fixture:
        bad = values_provenance_problems(_sidecar(Path(f"{values_path}.manifest.json")), values_path)
        if bad:
            raise SpecRefused(f"REFUSED: {W42_RULE}'s values file is not a pinned application (Q-186 m-3): {bad}")
    check_rows(spec, pin_row, _raw_sha(values_path), fixture, values_name=W.OUTPUT_NAME)
    cal = load_calendar(W, obj.values)
    parts = {k: build_part(spec.parts[k], fixture=fixture) for k in PART_NAMES}
    if space_digest(parts["space"]) != spec.parts["space"]["digest"]:
        raise PartRefused("REFUSED: the built space's digest is not the declared one (M-4)")
    check_levers(parts["space"])
    protocol = E.SS.Protocol(spec.measure, spec.blocks, spec.seeds, spec.horizon)       # refuses held-out blocks
    limit_names = tuple(lim["name"] for lim in obj.limits)
    if E.SS.protocol_sha256(protocol, spec.reread_seeds, limit_names) != spec.protocol_sha256:
        raise SpecRefused("REFUSED: the declared protocol sha256 is not the protocol's (Q-192's protocol_sha256 of the "
                          f"measure, blocks, seeds, horizon, re-read seeds and {W42_RULE}'s limits)")
    bad = heldout_problems(_existing_rows(out_dir / "variants.jsonl"))
    if bad:
        raise HeldOutRow(f"REFUSED: the variants ledger in {out_dir} already holds a held-out row: {bad[:3]}")
    check_once(sha, out_dir, name)
    limits = tuple(E.P.Limit(lim["name"], lim["bound"], lim["direction"]) for lim in obj.limits)
    ctx = Context(spec, E, W, obj, tuple(str(d) for d in cal.dates), cal, parts["space"], parts["gate"], tuple(spec.parts["gate"]["keys"]),
                  parts["schedule_builder"], parts["runner"], parts["playbook"], new_ledger(E), protocol, limits, sha,
                  writer, variants_writer, fixture)
    params = {"declaration_sha256": sha, "pin_row": pin_row, **process, "protocol_sha256": spec.protocol_sha256,
              "spec": spec.raw, "bindings": bound, "space_digest": spec.parts["space"]["digest"],
              "objective": {"values_sha256": obj.values_sha256, "values_row": spec.values_row,
                            "inactivity_guards": obj.guards},
              "no_harm": {"margin": spec.no_harm_margin, "margin_row": spec.margin_row},
              "round_spec": asdict(E.P.RoundSpec(**spec.round_kw)), "task": TASK}
    once_line = None
    if once is not None:                                    # m-5: recorded before the first cell, never rewritten
        from datetime import datetime, timezone
        once_line = record_once(sha, once, {"prereg_id": spec.prereg_id, "declaration": path.as_posix(), "pin_row": pin_row,
                                "commit": process["commit"], "run_id": os.environ.get(RUN_ID_ENV),
                                "results_dir": str(out_dir), "name": name,
                                "when": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        params["once_record"] = str(once)
        print(f"survey-once: {once_line}", flush=True)       # Q-186c: in the clean run's log, whatever follows
    try:
        designs = draw_survey(ctx)
        if ctx.ledger.protocol_sha256 != spec.protocol_sha256:
            raise SurveyRefused("the ledger's protocol is not the pinned declaration's (rb2-a)")
        params["ledger"] = {"protocol_sha256": ctx.ledger.protocol_sha256,
                            "declared": json.loads(json.dumps(E.SS.thaw(ctx.ledger.declared), default=str))}
        check_engine_rereads(ctx)
        record_baselines(ctx)
        read_all(ctx, designs, "survey")
        run_rounds(ctx)
        finalists = choose_finalists(ctx)
        em = emit(ctx, finalists, params=params, results_dir=out_dir, name=name)
    except Exception as exc:
        if ctx.ledger.rows:
            emit_failure(ctx, exc, params=params, results_dir=out_dir, name=name)
        raise
    return Outcome(sha, pin_row, finalists, list(ctx.records), list(ctx.floored), em["token"], em["list"],
                   em["list_sha256"], em["readings"], em["candidates"], em["variants"], ctx.ledger.counts(),
                   ctx.ledger, ctx.rounds, bound, once_line)


def declare_parts(parts: Mapping[str, Mapping[str, Any]], engine: Engine | None = None) -> dict[str, Any]:
    """The `parts` block of a declaration for these factory ids, parameters and data, each with its binding, the
    space with its built digest (a drafting aid: the declaration's author runs it; the red team reads the result)."""
    out = {}
    for k, v in parts.items():
        v = dict(v)
        v.setdefault("data", {})
        if k == "space":
            v["digest"] = space_digest(build_part(v, fixture=True))
        out[k] = dict(v, sha256=part_sha(v))
    out["engine"] = {"id": f"wave34+q192@{ENGINE_COMMIT}", "sha256": engine_sha(engine or Engine.default())}
    return out


__all__ = ["TASK", "ENGINE_COMMIT", "W42_RULE", "W42_SCRIPT", "W42_R2_NAMES", "ObjectiveRule", "ENTRY_SCRIPT", "DESIGN_ARM", "BASELINE_ROLE",
           "BASELINES", "AS_TRADED", "REFLECTED", "TRIGGER", "SEARCH_TAG", "SEARCH_LAST", "DELTA_STAR", "NOT_PAID",
           "DO_NOTHING", "W42_PUBLIC", "FIXTURE_PREFIX", "FIXTURE_ROW", "FIXTURE_TOKEN", "REAL_TOKEN", "DATA_LINKS",
           "ONCE_FILE", "INVOCATION_ENV", "VALUES_NAME", "DRIVER_MODULE", "PART_NAMES",
           "OBJECTIVE_MODULES", "SurveyRefused", "NotPinned", "SpecRefused", "PartRefused", "RunRepeated",
           "HeldOutRow", "LimitDisagrees", "RunOutput", "Engine", "Objective", "Spec", "Context", "Outcome", "closure_files",
           "code_closure", "part_sha", "engine_sha", "objective_code", "objective_code_sha", "driver_tree", "entry_file",
           "w42_script_file", "build_part", "data_path_problem", "check_data",
           "check_bindings", "searched_levers", "check_levers", "space_digest", "tree_problems",
           "untracked_modules", "invocation_problems", "check_process", "load_spec", "fixture_pin", "check_pinned",
           "margin_row_carries", "values_row_carries", "check_rows", "check_once", "once_location_problem",
           "head_pinned_commit", "once_marker", "check_once_record", "record_once", "known_local_appdata",
           "localappdata_problem", "lock_problem", "read_values", "values_provenance_problems", "load_objective",
           "load_calendar", "composite", "limit_value", "t_threshold", "new_ledger", "sessions_left", "validate_values", "book_check", "gate_check", "screen",
           "read_design", "read_all", "draw_survey", "check_engine_rereads", "record_baselines", "run_rounds",
           "beats_baselines", "limits_inside", "no_harm", "do_nothing_floor", "not_paid_floor", "passes_floors",
           "finalist_candidates", "plateau_step", "choose_finalists", "heldout_problems",
           "vendored_variants_writer", "variant_rows", "finalists_token", "emit", "emit_failure", "run_survey", "declare_parts"]
