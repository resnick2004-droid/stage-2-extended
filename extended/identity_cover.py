"""What each shared identity certifies (Q-111, E-113): **one declaration of the files a shared identity's token covers,
for every runner to import.** Under E-104 a runner waits on an identity's token and counts it held only where none of
the identity's covered files changed between the commit the token names and the run's commit
(`extended.identity_tokens.held`, Q-110). Three runners (RD-01's, RD-02's, F-03's) wait on the same shared identities;
each listed the covered files itself, the lists differed for the same id, and one lacked the identity's own script, so
an edit to the script after its token was still accepted. This module is that list, once:

    from extended import identity_cover as IC, identity_tokens as IT
    IT.held(text, "Q-80", repo, head, IC.cover("Q-80"))

**The rule.** An identity's cover is exactly

1. `BASE`: `extended/__init__.py` (the one door to the vendored engine, `use_vendored_stage2`) and the vendored
   snapshot's two manifests -- `vendor/MANIFEST_stage2.sha256` (every vendored byte: the engine, its scripts, its
   config and its registered results) and `vendor/DATA_MANIFEST_stage2.sha256` (the licensed bars and atlas). A new
   snapshot changes a manifest, so every identity must hold again on it. The manifests stand for everything under
   `vendor/`, which no cover lists file by file (`tests/test_vendor_integrity.py` holds the tree to them);
2. the identity's own script (`SCRIPT`): what runs and what compares;
3. every file of this repository the script imports, directly or transitively -- `identity/stage2_identity.py` among
   them wherever the script imports it. Every `import` and `from ... import` statement of a file counts, wherever it
   stands (module level, inside a function, under `if` or `try`): an import a run does not reach costs at most a
   re-run, one left out accepts code nobody checked. The closure is followed through this repository's own packages
   (`extended`, `identity`, `scripts`; any other file of the repository an import reaches too) and never into
   `vendor/` (the manifests stand for it).

`tests/test_identity_cover.py` computes 3 from the scripts' syntax (`imports`) and holds each cover equal to `BASE`
and that closure, so a cover cannot fall behind its code (nor keep a file its code no longer imports).

**The import model** (`imports`). A module name is looked up in every folder of `SEARCH` -- `vendor/stage2/scripts`,
`vendor/stage2`, the repository's root and `identity/`: what `use_vendored_stage2` and an identity script's own
preamble (the root and the script's folder) put on `sys.path` -- and **every** repository file it could name is
taken (the module file and the package `__init__.py` of each dotted prefix, in every folder, not only the one Python
would pick first). `from P import n` takes `P.n` too when that is a module; a relative import is looked up from the
importing file's folder. A name found in no folder must be the standard library's or installed outside the
repository, else it is reported. A call importing by name (`__import__`, `importlib.import_module`,
`runpy.run_module`) is followed when the name is a string literal and reported otherwise; a call importing by path
or running text (`spec_from_file_location`, `module_from_spec`, `runpy.run_path`, `exec`, `eval`, ...) is always
reported; so is a star import from a repository module. Every `sys.path` change met is listed (`PathEdit`), so the
test can hold `SEARCH` to the code: a new folder on the path is a new place a module can come from.

**Not covered** (the readings of Q-111):

* `DECISIONS.md`. The identities read it (the engine's read is authorised under their row) but the token's own row is
  written after the commit it names, so a cover holding the log would make every token fail;
* what the covered code reads at run time without importing it. Outside `vendor/` (the manifests) these identities
  read only the run's state -- the decision log, git's commit and status, and inside a clean run the read ledger they
  append to (`results/read_ledger.jsonl`) -- never code or a configuration of this repository. A file a runner's own
  reading reads belongs to that runner's own list;
* the run's arguments (`--paths 500`, `--cls all`, ...): the token's row says what was run, and the lead writes it
  only for the run its row names.

**A runner's own identities** -- RD-01's own (`identity/firms_identity.py`), RD-02's own (`pp_identity`) and its
two-worker check (`t10w2`), F-03's A0 (`identity/family_o_identity.py`) -- are not declared here: each runner declares
its own cover by this rule, `BASE`, the identity's script and its imports' closure (`imports(script)` computes it,
`uncovered(script, covered)` says what a list lacks), and may add files its reading needs. For a shared identity a
runner passes `cover(ident)`, never less (adding to it only makes its wait stricter). This module is the floor and the
convention, not those lists.

**What each certifies** (`CERTIFIES`, from its rows `ROWS`) is said once below. Nothing here reads a token, a result
or a bar. Pure Python (`ast`, `os`): importing it touches no `sys.path` and imports no engine.
"""
from __future__ import annotations

import ast
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, NamedTuple, Sequence

from extended import ROOT

#: in every cover, first: the door to the engine and the vendored snapshot's two manifests (code and data)
BASE: tuple[str, ...] = ("extended/__init__.py", "vendor/MANIFEST_stage2.sha256", "vendor/DATA_MANIFEST_stage2.sha256")
#: this repository's own packages, through which a closure is followed (and any other repository file it reaches)
PACKAGES: tuple[str, ...] = ("extended", "identity", "scripts")
#: the folders an import is looked up in (repository-relative; "." the root): what `use_vendored_stage2` and the
#: identity scripts' preamble put on `sys.path` (`tests/test_identity_cover.py` holds the code to it)
SEARCH: tuple[str, ...] = ("vendor/stage2/scripts", "vendor/stage2", ".", "identity")
#: the vendored tree: never followed, never covered file by file (the manifests in `BASE` stand for it)
VENDOR = "vendor"

#: each shared identity's own script
SCRIPT: dict[str, str] = {
    "Q-80": "identity/gate_identity.py",
    "Q-89": "identity/place_records_identity.py",
    "Q-93": "identity/user_beside_identity.py",
    "Q-101": "identity/replay_records_identity.py",
}
#: the decision rows that declare what each certifies and owe its run
ROWS: dict[str, tuple[str, ...]] = {
    "Q-80": ("E-049", "E-071"),
    "Q-89": ("E-055",),
    "Q-93": ("E-059", "E-084"),
    "Q-101": ("E-068",),
}
#: what each certifies, in its rows' words (the run its token's row names)
CERTIFIES: dict[str, str] = {
    "Q-80": ("Q-71's gate identities through the re-composed campaign (E-049; relaunched under E-055 so they cover "
             "Q-70's marked lines too): `identity/gate_identity.py --paths 500 --workers 1 --cls all` -- P-14's and "
             "P-16's registered gate calls through `extended.gate.run_gate` and `extended.campaign`, every arm (no "
             "class, the pass-through funded class, Q-71's seams at Topstep's values), on the registered paths file's "
             "first paths, both shifts, every `zero_edge_decomposition.PATH_COLS` column by `zd.path_problems`"),
    "Q-89": ("Q-70's place-recording identities (E-055): `identity/place_records_identity.py --paths 4 --only p16` "
             "and `--value-map 100` -- P-16's registered gate paths with recording off and on (every `PATH_COLS` "
             "column, the records consistent), and D-668's records basis (P-16's and P-14's trades a year by place "
             "against `u_value_map.csv`'s `trades_per_year_records`, the paths the registered files' first)"),
    "Q-93": ("Q-17's U1 replay with Q-76's declared funded class and Q-100's keywords (E-059 (1), E-084): "
             "`identity/user_beside_identity.py --u1-starts all --funded-cls both --q100 both` -- U1's start rows for "
             "P-14 and P-16, every start, every column of `user_journey.csv`'s start section by E-010's comparison, "
             "at the default, with the pass-through class and with `household_closure` and `seed_base` given, the "
             "given runs bit for bit the default's apart from the keys naming them"),
    "Q-101": ("Q-94's place recording on the U1 replay (E-068): `identity/replay_records_identity.py --u1-starts all "
              "--row E-068` -- U1's start rows for P-16 and P-14 with the replay recorder on, every start, E-010's "
              "comparison through Q-17's identity, and the records hold (Q-70's and Q-94's per-start checks)"),
}

#: each shared identity's cover: `BASE`, its script, then every repository file the script's imports reach
COVER: dict[str, tuple[str, ...]] = {
    "Q-80": (*BASE,
             "identity/gate_identity.py",
             "identity/stage2_identity.py",
             "extended/campaign.py",
             "extended/gate.py",
             "extended/place_fields.py",
             "extended/place_records.py",
             "extended/reader.py"),
    "Q-89": (*BASE,
             "identity/place_records_identity.py",
             "identity/gate_identity.py",
             "identity/stage2_identity.py",
             "extended/campaign.py",
             "extended/features.py",
             "extended/gate.py",
             "extended/place_fields.py",
             "extended/place_records.py",
             "extended/reader.py",
             "extended/synthetic_bars.py",
             "extended/walker.py"),
    "Q-93": (*BASE,
             "identity/user_beside_identity.py",
             "identity/stage2_identity.py",
             "extended/campaign.py",
             "extended/gate.py",
             "extended/openings.py",
             "extended/place_fields.py",
             "extended/place_records.py",
             "extended/reader.py",
             "extended/replay_records.py",
             "extended/user_beside.py",
             "extended/user_measures.py"),
    "Q-101": (*BASE,
              "identity/replay_records_identity.py",
              "identity/user_beside_identity.py",
              "identity/stage2_identity.py",
              "extended/campaign.py",
              "extended/gate.py",
              "extended/openings.py",
              "extended/place_fields.py",
              "extended/place_records.py",
              "extended/reader.py",
              "extended/replay_records.py",
              "extended/user_beside.py",
              "extended/user_measures.py"),
}


def cover(ident: str) -> tuple[str, ...]:
    """The covered paths of the shared identity `ident` (repository-relative, `/`-separated; `BASE` first, then its
    script), for `extended.identity_tokens.held`. Refused (`ValueError`): an id that is not one of `COVER`'s -- a
    runner's own identity declares its cover itself, by this module's rule."""
    if not isinstance(ident, str) or ident not in COVER:
        raise ValueError(f"{ident!r} is no shared identity of extended/identity_cover.py ({', '.join(COVER)}); a "
                         "runner's own identity declares its own cover by the same rule (BASE, its script, its "
                         "imports)")
    return COVER[ident]


# --- the import model ------------------------------------------------------------------------------------------------

class PathEdit(NamedTuple):
    """A change to `sys.path` in a file of a closure: where, the statement's source, and the source of the iterable
    of the innermost `for` loop around it ("" outside a loop)."""
    file: str
    line: int
    call: str
    loop: str


@dataclass(frozen=True)
class Closure:
    """`imports`' answer: the repository files the script's imports reach (the script included; sorted), every import
    the model could not resolve (`<file>:<line>: <why>`), and every `sys.path` change met."""
    script: str
    files: tuple[str, ...]
    unresolved: tuple[str, ...]
    path_edits: tuple[PathEdit, ...]


#: calls that import a module named by their first argument (followed when it is a string literal)
_BY_NAME = frozenset({"__import__", "import_module", "run_module"})
#: calls that import by path or run text: never resolved, always reported
_BY_PATH = frozenset({"spec_from_file_location", "spec_from_loader", "module_from_spec", "run_path", "load_source",
                      "SourceFileLoader", "SourcelessFileLoader", "exec_module", "load_module"})
#: builtins that run text (as a bare name only: `DataFrame.eval` is not one)
_BUILTIN_RUN = frozenset({"exec", "eval"})
_PATH_METHODS = frozenset({"insert", "append", "extend", "remove", "pop", "clear", "__setitem__", "__delitem__"})


def _abs(p: Path | str) -> Path:
    return Path(os.path.abspath(p))


def _under(p: Path | str, d: Path | str) -> bool:
    try:
        _abs(p).relative_to(_abs(d))
        return True
    except ValueError:
        return False


def _is_sys_path(node: ast.AST) -> bool:
    return (isinstance(node, ast.Attribute) and node.attr == "path" and isinstance(node.value, ast.Name)
            and node.value.id == "sys")


def _called(node: ast.Call) -> str:
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def _walk(node: ast.AST, loops: tuple[ast.AST, ...] = ()) -> Iterator[tuple[ast.AST, tuple[ast.AST, ...]]]:
    """Every node under `node`, each with the `for` loops around it (outermost first)."""
    for child in ast.iter_child_nodes(node):
        yield child, loops
        yield from _walk(child, loops + (child,) if isinstance(child, (ast.For, ast.AsyncFor)) else loops)


def _loop(src: str, loops: tuple[ast.AST, ...]) -> str:
    if not loops:
        return ""
    return ast.get_source_segment(src, loops[-1].iter) or ""


class _Folders:
    """The repository's folders as listed, so names match with their exact case (as Python's imports do on Windows,
    whose file system does not)."""

    def __init__(self) -> None:
        self._names: dict[Path, frozenset[str]] = {}

    def names(self, d: Path) -> frozenset[str]:
        if d not in self._names:
            try:
                self._names[d] = frozenset(os.listdir(d))
            except OSError:
                self._names[d] = frozenset()
        return self._names[d]

    def is_file(self, d: Path, name: str) -> bool:
        return name in self.names(d) and (d / name).is_file()

    def is_dir(self, d: Path, name: str) -> bool:
        return name in self.names(d) and (d / name).is_dir()

    def find(self, folders: Sequence[Path], dotted: str) -> tuple[list[Path], bool, bool]:
        """(every file importing `dotted` could execute, in every folder -- each prefix's module file and package
        `__init__.py`; whether the whole name is found in some folder; whether its first part is)."""
        parts = dotted.split(".")
        files: list[Path] = []
        full = top = False
        for e in folders:
            d = e
            for i, part in enumerate(parts):
                hit = False
                if self.is_file(d, f"{part}.py"):
                    files.append(d / f"{part}.py")
                    hit = True
                sub = self.is_dir(d, part)
                if sub:
                    hit = True
                    if self.is_file(d / part, "__init__.py"):
                        files.append(d / part / "__init__.py")
                if hit and i == 0:
                    top = True
                if hit and i == len(parts) - 1:
                    full = True
                if not sub:
                    break
                d = d / part
        return files, full, top


def _external(name: str, root: Path) -> str | None:
    """None when the top-level module `name` is the standard library's or installed outside the repository; else why
    the model cannot place it."""
    if name in sys.stdlib_module_names or name in sys.builtin_module_names:
        return None
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError) as exc:
        return f"{name} cannot be looked up ({type(exc).__name__}: {exc})"
    if spec is None:
        return f"{name} is in no folder of SEARCH and not installed"
    locs = [spec.origin] if spec.origin and spec.origin not in ("built-in", "frozen") else []
    locs += [str(x) for x in (spec.submodule_search_locations or [])]
    for loc in locs:
        if _under(loc, root) and not _under(loc, root / VENDOR):
            return (f"{name} is found only through this process's own path, inside the repository ({loc}): a folder "
                    "SEARCH does not model")
    return None


def imports(script: str, root: Path | str = ROOT, search: Sequence[str] = SEARCH) -> Closure:
    """The repository files `script`'s imports reach, directly or transitively, by the module docstring's model
    (`root`: the repository; `search`: the folders a module is looked up in, repository-relative). Refused
    (`ValueError`): a script that is not a file of the repository outside `vendor/`."""
    root = _abs(root)
    folders = [root if s in ("", ".") else root / s for s in search]
    listed = _Folders()
    start = _abs(root / script)
    if not _under(start, root) or _under(start, root / VENDOR) or not start.is_file():
        raise ValueError(f"{script!r}: not a file of this repository outside {VENDOR}/")
    seen: set[str] = set()
    todo = [start.relative_to(root).as_posix()]
    unresolved: list[str] = []
    edits: list[PathEdit] = []

    def take(paths: Sequence[Path]) -> None:
        for p in paths:
            if _under(p, root) and not _under(p, root / VENDOR):
                rel = _abs(p).relative_to(root).as_posix()
                if rel not in seen:
                    todo.append(rel)

    def absolute(rel: str, line: int, dotted: str) -> list[Path] | None:
        """The files an absolute import of `dotted` reaches (taken); None when it is not in `folders` (reported
        unless it is the standard library's or installed outside the repository)."""
        files, full, top = listed.find(folders, dotted)
        if full:
            take(files)
            return files
        if top:
            unresolved.append(f"{rel}:{line}: {dotted} is not found, though {dotted.split('.')[0]} is in a folder of "
                              "SEARCH")
            return None
        why = _external(dotted.split(".")[0], root)
        if why:
            unresolved.append(f"{rel}:{line}: {why}")
        return None

    while todo:
        rel = todo.pop()
        if rel in seen:
            continue
        seen.add(rel)
        path = root / rel
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=rel)
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError) as exc:
            unresolved.append(f"{rel}:0: cannot be read or parsed ({type(exc).__name__}: {exc})")
            continue
        for node, loops in _walk(tree):
            line = getattr(node, "lineno", 0)
            if isinstance(node, ast.Import):
                for a in node.names:
                    absolute(rel, line, a.name)
            elif isinstance(node, ast.ImportFrom) and node.level:
                base = path.parent
                for _ in range(node.level - 1):
                    base = base.parent
                if not _under(base, root):
                    unresolved.append(f"{rel}:{line}: a relative import above the repository's root")
                    continue
                if listed.is_file(base, "__init__.py"):
                    take([base / "__init__.py"])
                head = node.module or ""
                if head:
                    files, full, _ = listed.find([base], head)
                    if not full:
                        unresolved.append(f"{rel}:{line}: the relative import {'.' * node.level}{head} is not found")
                        continue
                    take(files)
                for a in node.names:
                    if a.name == "*":
                        unresolved.append(f"{rel}:{line}: a star import from a repository module")
                        continue
                    take(listed.find([base], f"{head}.{a.name}" if head else a.name)[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module == "sys" and any(a.name == "path" for a in node.names):
                    edits.append(PathEdit(rel, line, ast.get_source_segment(src, node) or "", _loop(src, loops)))
                files = absolute(rel, line, node.module or "")
                if files is None:
                    continue
                in_repo = [p for p in files if not _under(p, root / VENDOR)]
                for a in node.names:
                    if a.name == "*":
                        if in_repo:
                            unresolved.append(f"{rel}:{line}: a star import from a repository module")
                        continue
                    take(listed.find(folders, f"{node.module}.{a.name}")[0])
            elif isinstance(node, ast.Call):
                name = _called(node)
                if name in _BY_NAME:
                    arg = node.args[0] if node.args else None
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value \
                            and not arg.value.startswith("."):
                        absolute(rel, line, arg.value)
                    else:
                        unresolved.append(f"{rel}:{line}: a dynamic import by a name the syntax does not give "
                                          f"({ast.get_source_segment(src, node) or name})")
                elif name in _BY_PATH or (name in _BUILTIN_RUN and isinstance(node.func, ast.Name)):
                    unresolved.append(f"{rel}:{line}: code loaded by path or run from text "
                                      f"({ast.get_source_segment(src, node) or name})")
                elif (isinstance(node.func, ast.Attribute) and node.func.attr in _PATH_METHODS
                      and _is_sys_path(node.func.value)):
                    edits.append(PathEdit(rel, line, ast.get_source_segment(src, node) or "", _loop(src, loops)))
            elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Delete)):
                targets = node.targets if isinstance(node, (ast.Assign, ast.Delete)) else [node.target]
                for t in targets:
                    if _is_sys_path(t) or (isinstance(t, ast.Subscript) and _is_sys_path(t.value)):
                        edits.append(PathEdit(rel, line, ast.get_source_segment(src, node) or "", _loop(src, loops)))
    return Closure(start.relative_to(root).as_posix(), tuple(sorted(seen)), tuple(unresolved), tuple(sorted(edits)))


def uncovered(script: str, covered: Sequence[str], root: Path | str = ROOT, search: Sequence[str] = SEARCH
              ) -> list[str]:
    """Why `covered` falls short of the rule for the identity whose script is `script`: each path of `BASE`, the script
    and each repository file its imports reach that `covered` lacks (a folder covers what is under it, as `held` reads
    it), and each import the model could not resolve. [] when `covered` meets the rule."""
    if isinstance(covered, (str, bytes, os.PathLike)):
        raise TypeError("covered is a list of paths, not one path")
    have = [os.fspath(c).replace("\\", "/").rstrip("/") for c in covered]
    c = imports(script, root, search)
    out = [f"{p}: not covered" for p in (*BASE, *c.files) if not any(p == h or p.startswith(h + "/") for h in have)]
    return list(dict.fromkeys(out)) + [f"unresolved: {u}" for u in c.unresolved]


__all__ = ["BASE", "PACKAGES", "SEARCH", "VENDOR", "SCRIPT", "ROWS", "CERTIFIES", "COVER", "cover", "PathEdit",
           "Closure", "imports", "uncovered"]
