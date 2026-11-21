"""Q-134 (E-194): every test that reaches Stage 2's licensed data carries the `heavy` marker, so the root
`conftest.py`'s lock guard (Q-118, `extended.lock_guard`) skips it while another job holds `run.lock`.

E-194's breach: two tests of `tests/test_breakeven.py` marked `slow` only -- one re-walked ten real choice-block days,
one read A1's and A3's caches -- ran while F-03's run held the lock. `slow` is not `heavy`: the guard skips only `heavy`.

**The data** is the bar store `vendor/stage2/data/bars` and the atlas and walk caches `vendor/stage2/data/atlas`. A test
**reaches** it when (a static scan, `scan` below, of every `tests/test_*.py`):

1. **it names the data**: an expression in the test -- its body, its decorators, the fixtures it takes and the
   module's helper functions it calls, with their arguments bound from the call -- evaluates to a path under one of
   the two directories, rooted at the repository (`DATA / "bars"`, `ROOT / "vendor" / "stage2" / "data" / "atlas"`,
   `V.DEST / d for d in V.DATA_DIRS`, `C.MANIFEST`); a path under a temporary tree (`tmp_path / reader.STORE_REL`) is
   not the data;
2. **it calls a loader on the real tree**: `extended.reader.read_bars` / `read_walks` with neither `repo=` nor `**`
   keywords (the reader's default tree is this repository's);
3. **it runs a child that does**: a `[sys.executable, <script>, *argv]` command whose script is
   * a runner under `identity/` or `scripts/` (any repository script but the tests' own) whose source calls the
     reader's loaders or names the data (`RUNNER_READS`) -- unless the argv matches one of that runner's **light
     modes** in `LIGHT` (a synthetic mode, a refusal before any read, a plan that reads nothing), each with its reason;
   * a helper under `tests/` that names the data or calls a loader on the real tree (rules 1-2 over its whole file);
   * `-c <code>` whose code names the data (`DATA_TEXT`) or calls a loader without `repo=`.

A test that reaches the data and is not marked `heavy` fails `test_every_test_reaching_the_data_is_heavy`, unless it
is in `ALLOW` with its reason (a legitimate exception, kept short). Stale entries fail too: an `ALLOW` id that no
longer reaches the data, a `LIGHT` mode no spawn uses.

What the scan cannot see (said, not hidden): a production function called in-process that reads the data by its own
default (only the test module and the tests' helpers are followed); a script path or argv built at run time (an
argv item it cannot evaluate counts as no light mode -- the conservative side); a child that a child spawns. Q-134's
dynamic check (the fast tier run in a data-less clone under a tripwire, recorded in the hand-back) is the other half.

    python tests/test_heavy_marker_guard.py            # prints every test the scan finds reaching the data, and why
"""
from __future__ import annotations

import ast
import io
import itertools
import json
import os
import re
import subprocess
import sys
import tarfile
from dataclasses import dataclass, field
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIRS = (("vendor", "stage2", "data", "bars"), ("vendor", "stage2", "data", "atlas"))
LOADERS = frozenset({"read_bars", "read_walks"})
READER = "extended/reader.py"
#: a runner's source that reads the data: the reader's loaders, its engine-read authorisation, the stores' names
RUNNER_READS = re.compile(r"""\bread_bars\(|\bread_walks\(|\bauthorise_engine_read\(|\bSTORE_REL\b|\bATLAS_REL\b"""
                          r"""|data/bars|data/atlas|["']data["']\s*\)?\s*/\s*["'](?:bars|atlas)["']""")
#: a `-c` child's code that names the data or calls a loader without `repo=`
DATA_TEXT = re.compile(r"""data/bars|data/atlas|["']data["']\s*/\s*["'](?:bars|atlas)["']|\bDATA\s*/\s*["'](?:bars|atlas)"""
                       r"""["']|\bDATA_DIRS\b|\bread_(?:bars|walks)\((?![^)]*\brepo=)""")
#: the commit Q-134 started from (master at E-195): the scan must find E-194's breach there
PRE_CHANGE = "68a7aeb"
E194_BREACH = ("tests/test_breakeven.py::test_p14s_substitution_reaches_its_trades_and_only_inside_the_block",
               "tests/test_breakeven.py::test_the_rewalk_is_stage2s_on_the_first_real_days")

#: a runner's light modes: (tokens all present in the argv -- `!x` absent, `<no-args>` an empty argv, reason)
LIGHT: dict[str, tuple[tuple[tuple[str, ...], str], ...]] = {
    "identity/breakeven_identity.py": (
        (("--synthetic", "!--substitution", "!--smoke-days"), "E-011's synthetic days only; no bar or walk read"),),
    "identity/three_way_firm_identity.py": (
        (("--synthetic", "!--paths"), "gate_identity's synthetic blocks only; no bar or walk read (Q-185)"),),
    "identity/gate_identity.py": (
        (("--synthetic",), "synthetic blocks only; no bar or walk read"),
        (("--cls", "everything"), "argparse refuses the unknown arm before anything runs"),),
    "identity/walker_identity.py": (
        (("--synthetic", "!--smoke-days"), "synthetic days only; no bar or walk read"),
        (("--substitution", "!--smoke-days"),
         "probes only; reads A3's manifest.json (the cache key, metadata) when present, no bar or walk table"),),
    "identity/place_records_identity.py": (
        (("--synthetic",), "synthetic campaigns only"),
        (("--row", "E-99999"), "refused before any engine work: no such decision row"),),
    "identity/replay_records_identity.py": (
        (("<no-args>",), "argparse refuses: the identity needs its starts"),
        (("--u1-starts", "0"), "refused before anything is read: zero starts"),
        (("--funded-cls", "another"), "refused before anything is read: an unknown class"),
        (("--row", "E-99999"), "refused before anything is read: no such decision row"),),
    "identity/firms_identity.py": (
        (("--plan",), "prints the identity plan; reads nothing"),
        (("--starts", "!--row"), "refused without its decision row before any read"),),
    "identity/user_beside_identity.py": (
        (("--synthetic", "!--u1-starts"), "synthetic campaigns only; no bar or walk read"),
        (("--funded-cls", "--control"), "ap.error: the class option applies to the U1 comparison, not a control"),
        (("--funded-cls", "another"), "argparse refuses an unknown class before anything runs"),
        (("--q100", "--control"), "ap.error: --q100 applies to the U1 comparison, not a control"),
        (("--q100", "another"), "argparse refuses an unknown --q100 form before anything runs"),),
    "scripts/rd01_reading.py": (
        (("--plan",), "prints the guards' findings and what would run; reads nothing"),
        (("--purpose",), "argparse refuses: the three purposes run as one (no --purpose option)"),),
    "scripts/cl_reading.py": (
        (("--synthetic",), "toy campaigns (extended/cl_toy_inputs.py) into a temporary --results-dir; no bar or walk "
                           "read (Q-140, the RD-03 build review's B1)"),
        (("--starts", "!--synthetic"), "refused by starts_problem before any import: --starts is the synthetic "
                                       "window measurement's only"),),
    "scripts/breakeven_fidelity_2.py": (
        (("--starts", "4", "!--check"), "refused (Q-132) outside a clean run before any read"),
        (("--check", "--designs", "p13"), "refused (Q-132): an unknown design, before any read"),
        (("--check", "--designs", "p16,p16"), "refused (Q-132): a repeated design, before any read"),),
    "scripts/fo_opening.py": (
        (("--workers", "3"), "refused: more than two workers, before any read"),),
    "scripts/q108_calibrate.py": (
        (("<no-args>",), "refuses outside a clean run before any step (the test's env drops S2X_CLEAN_RUN)"),),
    "scripts/q126_calibrate.py": (
        (("<no-args>",), "refuses outside a clean run before any step (the test's env drops S2X_CLEAN_RUN)"),
        (("--part", "core"), "refuses outside a clean run before any step (the test's env drops S2X_CLEAN_RUN)"),),
    "scripts/q55_calibration.py": (
        (("<no-args>",), "refuses this tree's results outside a clean run before any read"),
        (("--pairs",), "the pairs supplied (synthetic): nothing extracted from the bars"),),
    "scripts/q16_p16_pairs.py": (
        (("--check-read",), "asks the reader and reads and writes nothing"),),
    "scripts/q82_validation.py": (
        (("<no-args>",), "refuses this tree's results outside a clean run before any read"),
        (("--check-read",), "asks the reader and reads nothing"),
        (("--pairs",), "the pairs and days supplied (synthetic): nothing extracted from the bars"),),
    "scripts/q16_calibrate.py": (
        (("--synthetic-only",), "synthetic nulls only"),),
}

#: tests that reach the data and are deliberately not `heavy`: id -> reason (a legitimate exception, kept short)
ALLOW: dict[str, str] = {
    "tests/test_vendor_integrity.py::test_data_matches_its_manifest_when_present":
        "the data's own integrity check: sha256 of each file streamed (constant memory, about 64 MB, seconds); loads "
        "no table and runs no engine, and is the hook's only check that the linked data are E-002's",
    "tests/test_calendar_early_closes.py::test_the_file_rebuilds_byte_for_byte_from_the_rules_and_the_manifest":
        "reads the bar store's manifest.json only (metadata, no bar file), as the calendar's own build does",
    "tests/test_hooks.py::test_absolute_paths_under_vendor_are_denied":
        "a path under the bar store given as text to the vendor-protect hook (an Edit it must deny); nothing opened",
}


# ------------------------------------------------------------------------------------------------------ the values

@dataclass(frozen=True)
class P:
    """A path relative to the repository's root."""
    parts: tuple[str, ...]


@dataclass(frozen=True)
class S:
    """A string."""
    s: str


@dataclass(frozen=True)
class Q:
    """A sequence: each item a frozenset of its alternatives."""
    items: tuple[frozenset, ...]


EXE = S("\0sys.executable")
NONE: frozenset = frozenset()


def _join(base: P, tail: str) -> P | None:
    if re.match(r"^([A-Za-z]:)?[\\/]", tail):
        return None
    parts = list(base.parts)
    for x in re.split(r"[\\/]+", tail):
        if x in ("", "."):
            continue
        if x == "..":
            if not parts:
                return None
            parts.pop()
        else:
            parts.append(x)
    return P(tuple(parts))


def under_data(v) -> bool:
    return isinstance(v, P) and any(v.parts[:len(d)] == d for d in DATA_DIRS)


def _rel(v: P) -> str:
    return "/".join(v.parts)


# ------------------------------------------------------------------------------------------------- the repository

class Repo:
    """The scanned tree: its modules parsed on demand, top-level names resolved as the suite's `sys.path` does."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self._mods: dict[str, Mod | None] = {}
        self._text: dict[str, str | None] = {}

    def text(self, rel: str) -> str | None:
        if rel not in self._text:
            p = self.root / rel
            self._text[rel] = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None
        return self._text[rel]

    def mod(self, rel: str) -> Mod | None:
        if rel not in self._mods:
            self._mods[rel] = None
            src = self.text(rel)
            if src is not None:
                try:
                    self._mods[rel] = Mod(self, rel, ast.parse(src))
                except SyntaxError:
                    self._mods[rel] = None
        return self._mods[rel]

    def resolve(self, name: str) -> str | None:
        """A module name to its file (relative), or None when it is not this repository's."""
        if name == "extended":
            return "extended/__init__.py"
        if name.startswith("extended."):
            rel = name.replace(".", "/") + ".py"
            return rel if (self.root / rel).is_file() else None
        if "." in name:
            return None
        for d in ("scripts", "identity", "tests", ""):
            rel = f"{d}/{name}.py" if d else f"{name}.py"
            if (self.root / rel).is_file():
                return rel
        return None


class Mod:
    def __init__(self, repo: Repo, rel: str, tree: ast.Module):
        self.repo, self.rel, self.tree = repo, rel, tree
        self.consts: dict[str, list[ast.expr]] = {}
        self.funcs: dict[str, ast.FunctionDef] = {}
        self.imports: dict[str, tuple] = {}
        for n in tree.body:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        self.consts.setdefault(t.id, []).append(n.value)
            elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None:
                self.consts.setdefault(n.target.id, []).append(n.value)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.funcs[n.name] = n
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    rel_ = repo.resolve(a.name)
                    if rel_:
                        self.imports[a.asname or a.name] = ("mod", rel_)
            elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
                for a in n.names:
                    sub = repo.resolve(f"{n.module}.{a.name}") if n.module == "extended" else None
                    if sub:
                        self.imports[a.asname or a.name] = ("mod", sub)
                    else:
                        base = repo.resolve(n.module)
                        if base:
                            self.imports[a.asname or a.name] = ("sym", base, a.name)

    def is_fixture(self, name: str) -> bool:
        f = self.funcs.get(name)
        return f is not None and any("fixture" in ast.unparse(d) for d in f.decorator_list)


# --------------------------------------------------------------------------------------------------- the evaluator

class Ev:
    def __init__(self, repo: Repo):
        self.repo = repo
        self._busy: set = set()
        self._const: dict = {}

    def const(self, mod: Mod, name: str) -> frozenset:
        key = (mod.rel, name)
        if key in self._const:
            return self._const[key]
        if key in self._busy:
            return NONE
        self._busy.add(key)
        try:
            if name == "__file__":
                out = frozenset({P(tuple(mod.rel.split("/")))})
            elif name in mod.consts:
                out = frozenset().union(*(self.ev(e, mod, {}) for e in mod.consts[name]))
            elif name in mod.imports and mod.imports[name][0] == "sym":
                other = self.repo.mod(mod.imports[name][1])
                out = self.const(other, mod.imports[name][2]) if other else NONE
            else:
                out = NONE
        finally:
            self._busy.discard(key)
        self._const[key] = out
        return out

    def expand(self, elts: list[ast.expr], mod: Mod, scope: dict, cap: int = 64) -> list[tuple[frozenset, ...]]:
        """A sequence's items, one tuple per alternative of its starred parts (`*argv` bound to several lists)."""
        alts: list[tuple[frozenset, ...]] = [()]
        for e in elts:
            if isinstance(e, ast.Starred):
                seqs = [v for v in self.ev(e.value, mod, scope) if isinstance(v, Q)]
                tails = [q.items for q in seqs] or [(frozenset({S("\0?*")}),)]
                alts = [a + t for a in alts for t in tails][:cap]
            else:
                v = self.ev(e, mod, scope)
                alts = [a + (v,) for a in alts]
        return alts

    def module_of(self, node: ast.expr, mod: Mod, scope: dict) -> Mod | None:
        if isinstance(node, ast.Name) and node.id not in scope and node.id in mod.imports:
            imp = mod.imports[node.id]
            if imp[0] == "mod":
                return self.repo.mod(imp[1])
        return None

    def ev(self, node: ast.expr | None, mod: Mod, scope: dict) -> frozenset:
        if node is None:
            return NONE
        if isinstance(node, ast.Constant):
            return frozenset({S(node.value)}) if isinstance(node.value, str) else NONE
        if isinstance(node, ast.Name):
            if node.id in scope:
                return scope[node.id]
            return self.const(mod, node.id)
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "sys" and node.attr == "executable":
                return frozenset({EXE})
            other = self.module_of(node.value, mod, scope)
            if other is not None:
                return self.const(other, node.attr)
            if node.attr == "parent":
                return frozenset(P(v.parts[:-1]) for v in self.ev(node.value, mod, scope)
                                 if isinstance(v, P) and v.parts)
            return NONE
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            out = set()
            for a in self.ev(node.left, mod, scope):
                for b in self.ev(node.right, mod, scope):
                    if isinstance(a, P) and isinstance(b, S):
                        j = _join(a, b.s)
                        if j is not None:
                            out.add(j)
            return frozenset(out)
        if isinstance(node, (ast.Tuple, ast.List)):
            return frozenset(Q(items) for items in self.expand(node.elts, mod, scope))
        if isinstance(node, ast.IfExp):
            return self.ev(node.body, mod, scope) | self.ev(node.orelse, mod, scope)
        if isinstance(node, ast.Call):
            f, args = node.func, node.args
            fname = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
            if isinstance(f, ast.Name) and f.id in ("Path", "PurePath", "PureWindowsPath", "PurePosixPath") or (
                    isinstance(f, ast.Attribute) and f.attr == "Path"):
                return frozenset(v for v in self.ev(args[0], mod, scope) if isinstance(v, P)) if args else NONE
            if fname in ("str", "fspath", "dedent") and args:
                return self.ev(args[0], mod, scope)
            if fname == "map" and len(args) == 2:
                return self.ev(args[1], mod, scope)
            if isinstance(f, ast.Attribute) and f.attr in ("resolve", "absolute", "expanduser", "as_posix",
                                                           "format", "strip"):
                return frozenset(v for v in self.ev(f.value, mod, scope) if isinstance(v, (P, S)))
            if isinstance(f, ast.Attribute) and f.attr == "joinpath":
                out = set()
                for a in self.ev(f.value, mod, scope):
                    for b in (self.ev(args[0], mod, scope) if len(args) == 1 else NONE):
                        if isinstance(a, P) and isinstance(b, S) and (j := _join(a, b.s)) is not None:
                            out.add(j)
                return frozenset(out)
            return NONE
        return NONE


# ------------------------------------------------------------------------------------------------------ the scanner

@dataclass
class Found:
    test: str
    marks: frozenset
    reasons: list[str] = field(default_factory=list)
    light: list[str] = field(default_factory=list)


def _marks(decorators: list[ast.expr]) -> set[str]:
    out = set()
    for d in decorators:
        node = d.func if isinstance(d, ast.Call) else d
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute) and node.value.attr == "mark":
            out.add(node.attr)
    return out


def _module_marks(mod: Mod) -> set[str]:
    out = set()
    for e in mod.consts.get("pytestmark", []):
        out |= _marks(list(e.elts) if isinstance(e, (ast.List, ast.Tuple)) else [e])
    return out


def _local_scope(fn: ast.AST, mod: Mod, ev: Ev, binding: dict) -> dict:
    scope = dict(binding)
    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        a = fn.args
        pos = [*a.posonlyargs, *a.args]
        for arg, default in zip(pos[len(pos) - len(a.defaults):], a.defaults):
            scope.setdefault(arg.arg, ev.ev(default, mod, {}))
        for arg, default in zip(a.kwonlyargs, a.kw_defaults):
            if default is not None:
                scope.setdefault(arg.arg, ev.ev(default, mod, {}))
        for arg in [*pos, *a.kwonlyargs, *([a.vararg] if a.vararg else []), *([a.kwarg] if a.kwarg else [])]:
            scope.setdefault(arg.arg, NONE)            # an unbound parameter is unknown, never a module name
    for _ in range(2):
        for n in ast.walk(fn):
            if isinstance(n, ast.Assign):
                vals = ev.ev(n.value, mod, scope)
                for t in n.targets:
                    if isinstance(t, ast.Name) and t.id not in binding:
                        scope[t.id] = scope.get(t.id, NONE) | vals
            elif isinstance(n, (ast.For, ast.comprehension)) and isinstance(n.target, ast.Name):
                elems = set()
                for q in ev.ev(n.iter, mod, scope):
                    if isinstance(q, Q):
                        for it in q.items:
                            elems |= it
                if elems and n.target.id not in binding:
                    scope[n.target.id] = scope.get(n.target.id, NONE) | frozenset(elems)
    return scope


def _bind(fn: ast.FunctionDef, call: ast.Call, mod: Mod, ev: Ev, scope: dict) -> dict:
    """The callee's parameters from the call's arguments, evaluated in the caller's scope."""
    a = fn.args
    pos = [x.arg for x in [*a.posonlyargs, *a.args]]
    out: dict = {}
    alts = ev.expand(call.args, mod, scope)
    for i, name in enumerate(pos):
        if all(len(x) > i for x in alts):
            out[name] = frozenset().union(*(x[i] for x in alts))
    if a.vararg is not None:
        out[a.vararg.arg] = frozenset(Q(tuple(x[len(pos):])) for x in alts)
    for k in call.keywords:
        if k.arg is not None:
            out[k.arg] = ev.ev(k.value, mod, scope)
    return out


def _argvs(q: Q, cap: int = 64) -> list[tuple]:
    """The concrete argvs of a command (each item one of its alternatives; an unknown item is "\\0?")."""
    choices = [sorted(it, key=repr) if it else [S("\0?")] for it in q.items]
    out = []
    for combo in itertools.product(*choices):
        out.append(combo)
        if len(out) >= cap:
            break
    return out


class Scanner:
    def __init__(self, repo: Repo, light: dict = LIGHT):
        self.repo, self.ev, self.light = repo, Ev(repo), light
        self._helper: dict[str, list[str]] = {}
        self.light_used: set[tuple[str, int]] = set()

    # -- a runner's light modes
    def runner_reads(self, rel: str) -> bool:
        src = self.repo.text(rel)
        return bool(src and RUNNER_READS.search(src))

    def light_mode(self, rel: str, args: list[str]) -> str | None:
        for i, (tokens, reason) in enumerate(self.light.get(rel, ())):
            ok = True
            for t in tokens:
                if t == "<no-args>":
                    ok &= not args
                elif t.startswith("!"):
                    ok &= t[1:] not in args
                else:
                    ok &= t in args
            if ok:
                self.light_used.add((rel, i))
                return reason
        return None

    # -- a helper under tests/ (rules 1 and 2 over its whole file)
    def helper(self, rel: str) -> list[str]:
        if rel not in self._helper:
            self._helper[rel] = []
            mod = self.repo.mod(rel)
            if mod is not None:
                found = Found(rel, frozenset())
                self.walk(mod.tree, mod, {}, found, depth=0, seen=set(), follow=False)
                self._helper[rel] = found.reasons
        return self._helper[rel]

    # -- one command
    def command(self, q: Q, mod: Mod, found: Found) -> None:
        for argv in _argvs(q):
            if argv[0] != EXE:
                return
            rest = list(argv[1:])
            while rest and isinstance(rest[0], S) and rest[0].s.startswith("-") and rest[0].s not in ("-c", "-m"):
                rest.pop(0)
            if not rest:
                continue
            head = rest[0]
            if isinstance(head, S) and head.s == "-c":
                code = rest[1].s if len(rest) > 1 and isinstance(rest[1], S) else ""
                if DATA_TEXT.search(code):
                    found.reasons.append(f"runs a `-c` child whose code names the data or calls a loader without repo=")
                continue
            if not isinstance(head, P) or not head.parts or not head.parts[-1].endswith(".py"):
                continue
            rel = _rel(head)
            args = [x.s if isinstance(x, S) else "\0?" for x in rest[1:]]
            shown = " ".join("?" if a.startswith("\0") else a for a in args)
            if head.parts[0] == "tests":
                for r in self.helper(rel):
                    found.reasons.append(f"runs {rel}, which {r}")
                continue
            if not self.runner_reads(rel):
                continue
            mode = self.light_mode(rel, args)
            if mode is None:
                found.reasons.append(f"runs {rel} {shown}".rstrip() + " (a runner that reads the data; no light mode)")
            else:
                found.light.append(f"{rel} {shown}: {mode}")

    # -- a function, its helpers and fixtures
    def walk(self, fn: ast.AST, mod: Mod, binding: dict, found: Found, depth: int, seen: set,
             follow: bool = True) -> None:
        scope = _local_scope(fn, mod, self.ev, binding)
        for n in ast.walk(fn):
            if isinstance(n, (ast.BinOp, ast.Name, ast.Attribute, ast.Call)) and not (
                    isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in mod.funcs):
                hit = [v for v in self.ev.ev(n, mod, scope) if under_data(v)]
                if hit:
                    found.reasons.append(f"names the data: `{ast.unparse(n)[:90]}` -> {_rel(hit[0])}")
            if isinstance(n, (ast.List, ast.Tuple)) and n.elts and isinstance(n.elts[0], ast.Attribute) and \
                    ast.unparse(n.elts[0]) == "sys.executable":
                for q in self.ev.ev(n, mod, scope):
                    if isinstance(q, Q):
                        self.command(q, mod, found)
            if isinstance(n, ast.Call):
                f = n.func
                name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
                if name in LOADERS and self._is_reader(f, mod) and not any(
                        k.arg is None or k.arg == "repo" for k in n.keywords):
                    found.reasons.append(f"calls the reader's {name} on this repository's tree (no repo=)")
                if follow and isinstance(f, ast.Name) and f.id in mod.funcs and f.id not in scope and depth < 4:
                    callee = mod.funcs[f.id]
                    bound = _bind(callee, n, mod, self.ev, scope)
                    key = (mod.rel, f.id, repr(sorted(bound.items(), key=lambda kv: kv[0])))
                    if key not in seen:
                        seen.add(key)
                        self.walk(callee, mod, bound, found, depth + 1, seen)

    def _is_reader(self, f: ast.expr, mod: Mod) -> bool:
        if isinstance(f, ast.Attribute):
            other = self.ev.module_of(f.value, mod, {})
            return other is not None and other.rel == READER
        imp = mod.imports.get(f.id) if isinstance(f, ast.Name) else None
        return bool(imp and imp[0] == "sym" and imp[1] == READER)

    # -- one test file
    def test_file(self, rel: str) -> list[Found]:
        mod = self.repo.mod(rel)
        if mod is None:
            return []
        base = _module_marks(mod)
        autouse = [f for name, f in mod.funcs.items()
                   if mod.is_fixture(name) and any("autouse" in ast.unparse(d) for d in f.decorator_list)]
        out = []
        for node in mod.tree.body:
            cases: list[tuple[ast.FunctionDef, set[str]]] = []
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                cases.append((node, set()))
            elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                cls_marks = _marks(node.decorator_list)
                for e in node.body:
                    if isinstance(e, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "pytestmark"
                                                         for t in e.targets):
                        cls_marks |= _marks(list(e.value.elts) if isinstance(e.value, (ast.List, ast.Tuple))
                                            else [e.value])
                cases += [(e, cls_marks) for e in node.body
                          if isinstance(e, (ast.FunctionDef, ast.AsyncFunctionDef)) and e.name.startswith("test")]
            for fn, extra in cases:
                found = Found(f"{rel}::{fn.name}", frozenset(base | extra | _marks(fn.decorator_list)))
                for binding in self._params(fn, mod):
                    seen: set = set()
                    for d in fn.decorator_list:
                        self.walk(d, mod, {}, found, 0, seen, follow=False)
                    self.walk(fn, mod, binding, found, 0, seen)
                    for fx in self._fixtures(fn, mod) + autouse:
                        self.walk(fx, mod, {}, found, 1, seen)
                found.reasons = list(dict.fromkeys(found.reasons))
                found.light = list(dict.fromkeys(found.light))
                out.append(found)
        return out

    def _fixtures(self, fn: ast.FunctionDef, mod: Mod, depth: int = 0) -> list[ast.FunctionDef]:
        out = []
        for a in [*fn.args.posonlyargs, *fn.args.args]:
            if mod.is_fixture(a.arg) and depth < 6:
                fx = mod.funcs[a.arg]
                out += [fx, *self._fixtures(fx, mod, depth + 1)]
        return out

    def _params(self, fn: ast.FunctionDef, mod: Mod, cap: int = 200) -> list[dict]:
        """One binding per parametrize combination (else one empty binding)."""
        axes = []
        for d in fn.decorator_list:
            if not (isinstance(d, ast.Call) and ast.unparse(d.func).endswith("mark.parametrize") and len(d.args) >= 2):
                continue
            names_v = [v for v in self.ev.ev(d.args[0], mod, {}) if isinstance(v, (S, Q))]
            if not names_v:
                continue
            nv = names_v[0]
            names = ([x.strip() for x in nv.s.split(",")] if isinstance(nv, S)
                     else [next(iter(it)).s for it in nv.items if it and isinstance(next(iter(it)), S)])
            rows = []
            for q in self.ev.ev(d.args[1], mod, {}):
                if isinstance(q, Q):
                    for item in q.items:
                        if len(names) == 1:
                            rows.append({names[0]: item})
                        else:
                            row = {}
                            for v in item:
                                if isinstance(v, Q) and len(v.items) == len(names):
                                    row = dict(zip(names, v.items))
                            rows.append(row)
            axes.append(rows or [{}])
        out = []
        for combo in itertools.product(*axes):
            b: dict = {}
            for row in combo:
                b.update(row)
            out.append(b)
            if len(out) >= cap:
                break
        return out or [{}]


def scan(root: Path | str = ROOT, light: dict = LIGHT) -> tuple[list[Found], Scanner]:
    """Every test of `root`'s `tests/test_*.py` with what makes it reach the data (empty when nothing does)."""
    repo = Repo(Path(root))
    sc = Scanner(repo, light)
    found = []
    for p in sorted((Path(root) / "tests").glob("test_*.py")):
        found += sc.test_file(p.relative_to(root).as_posix())
    return found, sc


def offenders(found: list[Found], allow: dict = ALLOW) -> list[Found]:
    return [f for f in found if f.reasons and "heavy" not in f.marks and f.test not in allow]


def _report(found: list[Found]) -> str:
    lines = []
    for f in found:
        if f.reasons:
            tag = "heavy" if "heavy" in f.marks else "ALLOW" if f.test in ALLOW else "MISSING heavy"
            lines.append(f"{tag:14s} {f.test}  [{', '.join(sorted(f.marks)) or 'no marker'}]")
            lines += [f"{'':14s}   - {r}" for r in f.reasons[:4]]
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------------- the guard

@pytest.fixture(scope="module")
def tree_scan():
    return scan(ROOT)


def test_every_test_reaching_the_data_is_heavy(tree_scan):
    found, _ = tree_scan
    bad = offenders(found)
    assert not bad, "tests that reach Stage 2's data without the `heavy` marker (Q-134):\n" + _report(bad)


def test_the_allow_list_and_the_light_modes_are_live(tree_scan):
    """A stale exception fails: every ALLOW id is a test that still reaches the data, every LIGHT mode is used."""
    found, sc = tree_scan
    reaching = {f.test for f in found if f.reasons}
    assert not set(ALLOW) - reaching, sorted(set(ALLOW) - reaching)
    unused = [(rel, LIGHT[rel][i][0]) for rel in LIGHT for i in range(len(LIGHT[rel])) if (rel, i) not in sc.light_used]
    assert not unused, unused
    for rel in LIGHT:
        assert sc.runner_reads(rel), f"{rel} no longer reads the data: its LIGHT entry is stale"


def test_the_scan_sees_the_known_readers(tree_scan):
    """Not vacuous: the scan finds the identities and readings this repository runs on the data (E-024's slow
    identities among them), and E-194's two tests."""
    found, _ = tree_scan
    reaching = {f.test for f in found if f.reasons}
    for t in (*E194_BREACH, "tests/test_stage2_identity.py::test_p14_and_p16_reproduced",
              "tests/test_extended_gate.py::test_the_adapter_reproduces_p14_and_p16_registered_gate_paths_at_four_paths",
              "tests/test_pp_identity.py::test_t8_the_reference_policy_reproduces_the_registered_rows_at_4_paths_and_4_starts",
              "tests/test_rd01_identity.py::test_t8_items_1_to_3_at_4_starts_and_4_paths",
              "tests/test_family_o_stage_c.py::test_t12_a0_at_four_paths_and_four_starts"):
        assert t in reaching, t
    for t in ("tests/test_breakeven.py::test_the_rewalk_on_synthetic_days",
              "tests/test_walker_stage2.py::test_the_walker_is_stage2s_walk_on_synthetic_days",
              "tests/test_family_o_grid.py::test_the_reader_grid_by_year_on_a_store_is_the_one_shot_grid"):
        assert t not in reaching, t                       # synthetic: no false alarm


def test_the_scan_fails_on_the_tree_before_q134(tmp_path):
    """The guard's own check: on master as Q-134 found it (`PRE_CHANGE`), the scan finds E-194's two tests -- and
    others -- reaching the data without `heavy`."""
    have = subprocess.run(["git", "cat-file", "-e", f"{PRE_CHANGE}^{{commit}}"], cwd=ROOT, capture_output=True)
    if have.returncode:
        pytest.skip(f"{PRE_CHANGE} is not in this clone's history")
    tar = subprocess.run(["git", "archive", "--format=tar", PRE_CHANGE, "tests", "identity", "scripts", "extended"],
                         cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(tmp_path, filter="data")
    found, _ = scan(tmp_path, LIGHT)
    bad = {f.test for f in offenders(found, {})}
    for t in E194_BREACH:
        assert t in bad, (t, sorted(bad))
    assert len(bad) > len(E194_BREACH)


#: a child pytest's plugin: the lock guard pointed at a fake main root, and every collected item's skip reason printed
SKIP_PLUGIN = '''
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.environ["Q134_ROOT"])


def pytest_configure(config):
    from extended import lock_guard
    main = Path(os.environ["Q134_FAKE_MAIN"])
    lock_guard.main_root = lambda start=None: main


def pytest_collection_finish(session):
    out = {}
    for item in session.items:
        m = item.get_closest_marker("skip")
        out[item.nodeid] = m.kwargs.get("reason") if m else None
    Path(os.environ["Q134_OUT"]).write_text(json.dumps(out), encoding="utf-8")
'''


def _collected_skips(tmp_path: Path, files: list[str], lock_job: str | None) -> dict:
    main = tmp_path / ("main_locked" if lock_job else "main_free")
    main.mkdir()
    if lock_job:
        (main / "run.lock").write_text(json.dumps({"job": lock_job, "task": "Q-134", "holder": "a test", "pid": 1}),
                                       encoding="utf-8")
    (tmp_path / "q134_skip_plugin.py").write_text(SKIP_PLUGIN, encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in ("S2X_LOCK_HOLDER", "PYTEST_ADDOPTS")}
    out = main / "skips.json"
    env.update(Q134_ROOT=str(ROOT), Q134_FAKE_MAIN=str(main), Q134_OUT=str(out), PYTHONPATH=str(tmp_path),
               PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "q134_skip_plugin",
                        "-p", "no:cacheprovider", *files], cwd=ROOT, capture_output=True, text=True, timeout=600,
                       env=env)
    assert r.returncode == 0 and out.is_file(), r.stdout[-3000:] + r.stderr[-3000:]
    return json.loads(out.read_text(encoding="utf-8"))


def test_every_heavy_reader_is_skipped_while_another_job_holds_the_lock(tree_scan, tmp_path):
    """Q-134's step 4: with a fake `run.lock` held by another job at the (fake) main root, the root conftest's guard
    skips every test the scan finds reaching the data and marked `heavy` -- E-194's two among them -- with the reason
    naming the lock and its job; with no lock, the guard skips none of them. Collection only: no test body runs."""
    found, _ = tree_scan
    heavy = sorted(f.test for f in found if f.reasons and "heavy" in f.marks)
    assert set(E194_BREACH) <= set(heavy)
    files = sorted({t.split("::")[0] for t in heavy})
    held = _collected_skips(tmp_path, files, "q134-fake-job")
    want = "heavy test skipped: run.lock held by q134-fake-job (only the lock's holder may run heavy tests)"
    assert {t: held.get(t) for t in heavy} == {t: want for t in heavy}
    free = _collected_skips(tmp_path, files, None)
    assert all(free.get(t) is None for t in heavy), {t: free.get(t) for t in heavy}


# ------------------------------------------------------------------------------- the scanner on a synthetic tree

TOY_RUNNER = '''
from extended import reader
def main(argv):
    if "--synthetic" in argv:
        return 0
    return reader.read_bars("2020-01-02", "2020-01-03")
'''

TOY_HELPER_REAL = '''
import sys
from pathlib import Path
from extended import reader
ROOT = Path(__file__).resolve().parent.parent
print((ROOT / reader.STORE_REL / "NQ" / "bars.parquet").stat())
'''

TOY_HELPER_SYNTH = '''
import sys
from pathlib import Path
from extended import reader
WORK = Path(sys.argv[1])
store = WORK / reader.STORE_REL / "NQ"
reader.read_bars("2020-01-02", "2020-01-03", repo=WORK)
'''

TOY_TESTS = '''
import subprocess, sys
from pathlib import Path
import pytest
from extended import reader
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "vendor" / "stage2" / "data"
SCRIPT = ROOT / "identity" / "toy_identity.py"
SNIPPET = """
from pathlib import Path
print(Path("vendor/stage2/data/atlas/A3/walks.parquet"))
"""

def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args])

@pytest.fixture()
def store():
    return DATA / "atlas" / "A1"

@pytest.mark.slow
def test_idiom_slow_only():
    if not (DATA / "bars").is_dir():
        pytest.skip("no bars")

@pytest.mark.heavy
def test_idiom_heavy():
    if not (DATA / "bars").is_dir():
        pytest.skip("no bars")

def test_runner_light():
    run("--synthetic")

def test_runner_real():
    run("--smoke-days", "10")

@pytest.mark.parametrize("argv", [["--synthetic"], ["--row", "E-1"]])
def test_runner_param(argv):
    subprocess.run([sys.executable, str(SCRIPT), *argv])

def test_fixture(store):
    pass

def test_loader_no_repo():
    reader.read_bars("2020-01-02", "2020-01-03")

def test_loader_tmp(tmp_path):
    reader.read_bars("2020-01-02", "2020-01-03", repo=tmp_path)
    (tmp_path / reader.STORE_REL).mkdir(parents=True)

def test_helper_real():
    subprocess.run([sys.executable, str(ROOT / "tests" / "toy_real.py")])

def test_helper_synth(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "tests" / "toy_synth.py"), str(tmp_path)])

def test_dash_c():
    subprocess.run([sys.executable, "-c", SNIPPET])

def test_nothing():
    assert (ROOT / "DECISIONS.md").name

@pytest.mark.skipif(not (DATA / "atlas" / "A3" / "manifest.json").exists(), reason="x")
def test_decorator():
    pass
'''


@pytest.fixture()
def toy(tmp_path):
    for rel, text in (("tests/test_toy.py", TOY_TESTS), ("identity/toy_identity.py", TOY_RUNNER),
                      ("tests/toy_real.py", TOY_HELPER_REAL), ("tests/toy_synth.py", TOY_HELPER_SYNTH),
                      ("extended/__init__.py", (ROOT / "extended" / "__init__.py").read_text(encoding="utf-8")),
                      ("extended/reader.py", 'STORE_REL = "vendor/stage2/data/bars"\n'
                                             'ATLAS_REL = "vendor/stage2/data/atlas"\n'
                                             'def read_bars(*a, repo=None, **k): pass\n')):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    light = {"identity/toy_identity.py": ((("--synthetic",), "synthetic only"),)}
    found, _ = scan(tmp_path, light)
    return {f.test.split("::")[1]: f for f in found}


def test_the_scanner_on_a_synthetic_tree(toy):
    reach = {k for k, f in toy.items() if f.reasons}
    assert reach == {"test_idiom_slow_only", "test_idiom_heavy", "test_runner_real", "test_runner_param",
                     "test_fixture", "test_loader_no_repo", "test_helper_real", "test_dash_c", "test_decorator"}, reach
    assert {f.test.split("::")[1] for f in offenders(list(toy.values()), {})} == reach - {"test_idiom_heavy"}
    assert "no light mode" in toy["test_runner_param"].reasons[0] and "--row E-1" in toy["test_runner_param"].reasons[0]
    assert toy["test_runner_light"].light == ["identity/toy_identity.py --synthetic: synthetic only"]
    assert toy["test_idiom_slow_only"].marks == {"slow"}
    assert any("vendor/stage2/data/bars/NQ/bars.parquet" in r for r in toy["test_helper_real"].reasons)


def test_an_allow_list_entry_excuses_one_test(toy):
    found = list(toy.values())
    allow = {"tests/test_toy.py::test_loader_no_repo": "a reason"}
    assert "tests/test_toy.py::test_loader_no_repo" not in {f.test for f in offenders(found, allow)}
    assert "tests/test_toy.py::test_dash_c" in {f.test for f in offenders(found, allow)}


if __name__ == "__main__":
    found, sc = scan(ROOT)
    print(_report(found))
    print(f"\n{sum(1 for f in found if f.reasons)} of {len(found)} tests reach the data; "
          f"{len(offenders(found))} without `heavy` and not allowed")
