"""The pre-commit fast tier's tier and test selection (Q-209), from the commit's staged paths.

    python scripts/fasttier_select.py --explain            # what this tree's staged change would run, and why
    python scripts/fasttier_select.py --hook --out <file>  # the hook's call: prints the tier and its reason, writes the
                                                           # selected test files (pytest's @file) to <file>

**The tiers** (the same `-m "not slow and not heavy"` selection inside each; only the files differ):

* **T0, records only.** Every staged path is a Markdown record or review (RECORD_FILES, docs/reviews/**,
  docs/audits/**, docs/plans/**/*.md). Runs T0_ALWAYS (the tests that read the records: identity tokens, declarations
  fixed, the seed guard, reader*, the trace check, archive_queue, status, vendor integrity) and every test the graph
  below reaches from the staged records. In its own one-slot lane (`fasttier_lock.py --lane t0`), never behind a full run.
* **T1, a worker's code commit** (any tree but the main worktree). Runs ALWAYS (vendor integrity, declarations fixed,
  the seed guard, the reader seal, the heavy-marker guard) and every test the graph reaches from the staged paths.
* **T2, the full fast tier**: the main tree's code commits, every merge commit (MERGE_HEAD present), every FALLBACK
  (below), and a T1 whose selection is most of the tier (FULL_FRACTION). `scripts/fasttier_full.py` runs it on a
  branch's tip before hand-back; `scripts/check_verdicts.py` requires it on the tip.

**The pre-flight** (E-274; `--preflight-out`): before any tier's stage, the hook runs PREFLIGHT_GUARDS (the always-on
guards), the staged test files, and the tests that import or name a staged file directly (at most PREFLIGHT_DIRECT_MAX),
in the T0 lane. A failure refuses there, before the stage takes a slot of the shared line; the stage then still runs
everything it selects.

**The graph** (static; where it cannot tell, it selects). Every Python file under tests/, extended/, scripts/ and
identity/ (and the root) is parsed for three kinds of edge:

1. *imports* -- `import a.b`, `from a import b`, relative imports, `importlib.import_module("x")`, bare names resolved
   as the suite's sys.path inserts make them (scripts/, tests/, identity/, scripts/hooks/, the source's own folder),
   each package's `__init__.py` on the way included;
2. *names* -- a string literal (literals joined through `/` chains, `Path(...)` and `os.path.join(...)` included;
   backslashes read as slashes) holding the file's path, or its file name as a path component, or its dotted module
   name (`-m extended.x`). A bare stem is never a name: as a literal it is a word ("status");
3. *listings* -- each folder listing, bound to its own call: `path.glob(pattern)`, `path.rglob(pattern)`,
   `path.iterdir()`, `os.listdir/scandir/walk(folder)`, `glob.glob(pattern)`, `fnmatch.*(name, pattern)` (a constant
   pattern only). The folder is the receiver's constant parts (`repo / "prereg"` gives prereg), an f-string pattern
   reads each formatted part as `*`; a listing sees a file when its folder occurs among the file's folders and the
   rest matches its pattern. A recursive walk of a folder it cannot name, of everything (`base.rglob("*")`, `os.walk(d)`,
   `git ls-files`), makes the source *wide*: it sees every file, unless WALK_SCOPES bounds it by hand.

**What a change reaches.** A file's bytes differ only if it is staged, so the sources that *name* or *list* a staged
file are the first reached. From them behaviour spreads only as code runs: to every source that imports a reached file,
and to every source that names a reached Python file (a script run as a subprocess, a module loaded by path). A staged
test file is always selected. The selection is the test files (tests/**/test_*.py) reached.

**FALLBACK to T2** (never a smaller set): a staged conftest.py, pyproject.toml, .gitattributes, pytest/tox/setup
config, the git hooks or the hook installer, scripts/hooks/**, any fasttier_* file, .claude/ settings, anything under
vendor/ (refused by the hook anyway); a staged Python file that does not parse; a staged Python file under tests/ that
is not a test and that no test reaches (the graph cannot place it); a staged file under config/, prereg/, identity/,
results/ or data/ that no source names, imports or lists; any error of the selector itself (the hook then runs T2).

**What it does not see** (the red team's list): a file read through a path built only from variables, with no constant
part, by a source that neither names nor lists it; a dependency through a subprocess that is not Python (git reading
the repository: a test whose result depends on the committed history rather than on files); a test whose outcome
depends on a file only through the environment. A T1 commit can therefore pass with such a test broken; the branch tip's
T2 (`scripts/fasttier_full.py`, required by `check_verdicts.py`) and the main tree's merge gate catch it before master.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

RECORD_FILES = ("DECISIONS.md", "STATUS.md", "TASK_QUEUE.md", "PROGRESS.md", "PARKING_LOT.md")
RECORD_DIRS = ("docs/reviews/", "docs/audits/")
RECORD_GLOBS = ("docs/plans/*.md", "docs/plans/**/*.md")

#: run by every T1 (and T0): the guards whose failure no import edge would predict
ALWAYS = ("tests/test_vendor_integrity.py", "tests/test_declarations_fixed.py", "tests/test_seed_derivation_guard.py",
          "tests/test_reader.py", "tests/test_heavy_marker_guard.py")
#: run by every T0: the tests that read the records, named (the graph adds the rest)
T0_ALWAYS = ("tests/test_identity_tokens.py", "tests/test_declarations_fixed.py", "tests/test_seed_derivation_guard.py",
             "tests/test_reader*.py", "tests/test_trace_check.py", "tests/test_archive_queue.py", "tests/test_status.py",
             "tests/test_vendor_integrity.py")

#: E-274's always-on guards: the pre-flight runs them (and the nearest tests) before the tier's stage takes a slot
PREFLIGHT_GUARDS = ("tests/test_heavy_marker_guard.py", "tests/test_heavy_guard.py", "tests/test_seed_derivation_guard.py",
                    "tests/test_identity_tokens.py", "tests/test_declarations_fixed.py", "tests/test_git_scan.py",
                    "tests/test_trace_check.py", "tests/test_vendor_integrity.py", "tests/test_reader*.py")
#: the pre-flight adds the tests that import or name a staged file directly only when there are at most this many
PREFLIGHT_DIRECT_MAX = 10
#: a staged path matching any of these runs the full fast tier
FALLBACK_GLOBS = ("conftest.py", "*/conftest.py", "pyproject.toml", ".gitattributes", "pytest.ini", "tox.ini",
                  "setup.cfg", "scripts/pre-commit", "scripts/commit-msg", "scripts/post-commit",
                  "scripts/pre-merge-commit", "scripts/install_hooks.py", "scripts/hooks/*", "*fasttier_*",
                  "vendor/*", ".claude/settings*.json")
#: a staged file under one of these that no source names runs the full fast tier
NAMED_OR_FULL = ("config/", "prereg/", "identity/", "results/", "data/")
SOURCE_DIRS = ("tests", "extended", "scripts", "identity")
BARE_DIRS = ("scripts", "tests", "identity", "scripts/hooks", "")
#: a T1 selecting more than this share of the tier's test files runs the full (parallel) tier instead
FULL_FRACTION = 0.6

#: the walks the graph cannot bound from literals (rule 3), bounded by hand: a wide source listed here depends only on
#: the files matching its patterns (fnmatch on the repository path; `*` crosses folders). Every other wide non-test
#: source is listed in WALK_UNSCOPED with why, and depends on every file (tests/test_fasttier_select.py holds both).
WALK_SCOPES = {
    "extended/price_levels.py": ("*.csv", "*.tsv"),     # git ls-files of the index: the licence check's CSVs
    "scripts/vendor_stage2.py": ("vendor/*",),           # rglob of vendor/stage2 and its data folders
    "scripts/q126_calibrate.py": (),                     # rglob of a temporary folder it made itself
    "scripts/q108_calibrate.py": ("*.py",),              # git ls-files -- *.py: its provenance of every Python file
    "scripts/fasttier_select.py": ("*.py",),             # this graph: every Python file of the source folders
}
WALK_UNSCOPED = {
    "scripts/rd01_reading.py": "git ls-files of each covered folder, named by a wait's declaration",
    "tests/pp_run_check.py": "git ls-files of each wait's covered paths",
}
LIST_METHODS = ("iterdir", "glob", "rglob")                  # path.<m>(pattern): the receiver is the folder
MATCH_FUNCS = ("fnmatch", "fnmatchcase", "filter")             # fnmatch.<f>(name, pattern)
GLOB_CHARS = set("*?[")


@dataclass
class Source:
    rel: str
    imports: set[str] = field(default_factory=set)      # repository files it imports (resolved)
    literals: list[tuple[str, ...]] = field(default_factory=list)   # path-like literals, as components
    raw: set[str] = field(default_factory=set)          # every string literal, normalised
    #: its folder listings: (the folder's constant components or None if unknown, the pattern or None, recursive)
    listings: list = field(default_factory=list)
    wide: bool = False                                   # a walk whose folder and pattern bound nothing
    error: str | None = None


@dataclass
class Decision:
    tier: str
    reason: str
    tests: list[str] = field(default_factory=list)


class SelectionError(RuntimeError):
    pass


# ------------------------------------------------------------------------------------------------ paths

def _norm(s: str) -> str:
    s = s.replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return s


def _comps(s: str) -> tuple[str, ...]:
    return tuple(c for c in _norm(s).split("/") if c and c != ".")


def is_record(path: str) -> bool:
    p = _norm(path)
    return (p in RECORD_FILES or any(p.startswith(d) for d in RECORD_DIRS)
            or (p.endswith(".md") and p.startswith("docs/plans/")))


def fallback_reason(path: str) -> str | None:
    p = _norm(path)
    for g in FALLBACK_GLOBS:
        if fnmatch.fnmatchcase(p, g):
            return f"{p} matches {g}"
    return None


def is_test_file(rel: str) -> bool:
    p = PurePosixPath(_norm(rel))
    return p.parts[:1] == ("tests",) and p.name.startswith("test_") and p.suffix == ".py"


def module_names(rel: str) -> set[str]:
    """The names a Python file is imported or run under: dotted from the root, and its bare stem."""
    p = PurePosixPath(_norm(rel))
    if p.suffix != ".py":
        return set()
    parts = list(p.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    names = {".".join(parts)} if parts else set()
    if parts:
        names.add(parts[-1])
    return names


# ------------------------------------------------------------------------------------------------ parsing

def _joined(node: ast.AST) -> str | None:
    """The string a `/` chain, `Path(...)` or `os.path.join(...)` of string constants spells, constants only."""
    parts: list[str] = []

    def walk(n) -> bool:
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            parts.append(n.value)
            return True
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            left = walk(n.left)
            right = walk(n.right)
            return left or right
        return False

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        walk(node)
    elif isinstance(node, ast.Call):
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""
        if name in ("Path", "PurePath", "PurePosixPath", "join"):
            parts = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
    return "/".join(p.strip("/") for p in parts if p.strip("/")) if len(parts) >= 2 else None


def _resolve(name: str, src_rel: str, exists) -> set[str]:
    """The repository files `import name` (seen from `src_rel`) may load, packages' __init__ files included."""
    out: set[str] = set()
    parts = name.split(".")
    for k in range(1, len(parts) + 1):                    # a.b.c loads a/__init__, a/b/__init__, a/b/c
        stem = "/".join(parts[:k])
        for cand in (f"{stem}.py", f"{stem}/__init__.py"):
            if exists(cand):
                out.add(cand)
    if len(parts) == 1:                                   # a bare name: the suite's sys.path inserts
        here = str(PurePosixPath(src_rel).parent)
        for d in (*BARE_DIRS, here):
            d = "" if d in ("", ".") else d.rstrip("/") + "/"
            for cand in (f"{d}{name}.py", f"{d}{name}/__init__.py"):
                if exists(cand):
                    out.add(cand)
    return out


def _pattern(node) -> str | None:
    """A glob pattern from a string constant, or an f-string with each formatted part read as `*`."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return _norm(node.value)
    if isinstance(node, ast.JoinedStr):
        return _norm("".join(v.value if isinstance(v, ast.Constant) else "*" for v in node.values))
    return None


def _call_name(node: ast.Call) -> str:
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""


def _folder(node) -> tuple[str, ...] | None:
    """A folder's constant components: a string, a `/` chain (its constant parts), Path("a", "b"); else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return _comps(node.value) or None
    parts: list[str] = []

    def walk(n) -> None:
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            parts.extend(_comps(n.value))
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            walk(n.left)
            walk(n.right)

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        walk(node)
    elif isinstance(node, ast.Call) and _call_name(node) in ("Path", "PurePath", "PurePosixPath", "join"):
        for a in node.args:
            walk(a)
    return tuple(parts) or None


def _listing(node: ast.Call):
    """(folder, pattern, recursive) when the call lists a folder or matches names against a pattern, else None.
    `walk` is a directory walk only as os.walk or Path.walk() (W.walk is the engine's walker, ast.walk a syntax
    tree's)."""
    f = node.func
    name = _call_name(node)
    owner = f.value.id if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else None
    first = node.args[0] if node.args else None
    if owner == "os" and name in ("listdir", "scandir", "walk"):
        return (_folder(first) if first is not None else None, None, name == "walk")
    if owner == "glob" and name in ("glob", "iglob"):
        return (None, _pattern(first) if first is not None else None, True)
    if owner == "fnmatch" and name in MATCH_FUNCS:            # a name match, not a walk: only a constant pattern
        pattern = _pattern(node.args[1]) if len(node.args) > 1 else None
        return (None, pattern, False) if pattern else None
    if isinstance(f, ast.Attribute) and name in LIST_METHODS and owner not in ("ast", "os", "glob", "fnmatch"):
        return (_folder(f.value), _pattern(first) if first is not None else None, name == "rglob")
    if isinstance(f, ast.Attribute) and name == "walk" and not node.args and not node.keywords and owner not in (
            "ast", "os"):
        return (_folder(f.value), None, True)                # Path.walk()
    return None


def parse_source(root: Path, rel: str, exists) -> Source:
    s = Source(rel)
    try:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text, filename=rel)
    except (OSError, SyntaxError, ValueError) as e:
        s.error = f"{type(e).__name__}: {e}"
        return s
    pkg = list(PurePosixPath(rel).parent.parts)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                s.imports |= _resolve(a.name, rel, exists)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = pkg[: len(pkg) - (node.level - 1)] if node.level > 1 else pkg
                mod = ".".join([*base, *(node.module.split(".") if node.module else [])])
            else:
                mod = node.module or ""
            if mod:
                s.imports |= _resolve(mod, rel, exists)
            for a in node.names:
                if mod:
                    s.imports |= _resolve(f"{mod}.{a.name}", rel, exists)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            v = _norm(node.value)
            s.raw.add(v)
            if v == "ls-files":                             # git ls-files: the whole tree
                s.wide = True
        elif isinstance(node, (ast.BinOp, ast.Call)):
            j = _joined(node)
            if j:
                s.raw.add(_norm(j))
            if isinstance(node, ast.Call):
                if _call_name(node) in ("import_module", "__import__") and node.args and isinstance(
                        node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    s.imports |= _resolve(node.args[0].value, rel, exists)
                listing = _listing(node)
                if listing is not None:
                    folder, pattern, recursive = listing
                    s.listings.append(listing)
                    if folder is None and recursive and pattern in (None, "*", "**", "**/*"):
                        s.wide = True                       # a recursive walk of an unknown folder, of everything
    s.literals = [c for c in (_comps(v) for v in s.raw) if c]
    return s


# ------------------------------------------------------------------------------------------------ the graph

def _contiguous(needle: tuple[str, ...], hay: tuple[str, ...]) -> bool:
    n = len(needle)
    return n > 0 and any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def names_file(src: Source, path: str) -> bool:
    """Whether `src` names `path` (rule 2): a literal holding its path or its file name as a path component, or its
    dotted module name (`-m extended.x`). A bare stem is not a name here (`import x` and `import_module("x")` are
    import edges); as a bare literal it is a word ("status"), and reading it as the file selected most of the tier."""
    f = _comps(path)
    if not f:
        return False
    for lit in src.literals:
        if _contiguous(f, lit) or f[-1] in lit:
            return True
    mods = module_names(path)
    return bool({m for m in mods if "." in m} & src.raw)


def lists_file(src: Source, path: str) -> bool:
    """Whether one of `src`'s folder listings can see `path`: its folder occurs among the path's folders and the rest
    matches its pattern; with no folder known, the pattern matches the path; with neither, a literal of the source is
    one of the path's folders (the loose rule). A source in WALK_SCOPES sees exactly its declared patterns."""
    scope = WALK_SCOPES.get(src.rel)
    if scope is not None:
        return any(fnmatch.fnmatchcase(path, pat) for pat in scope)
    if src.wide:
        return True
    f = _comps(path)
    joined = "/".join(f)
    for folder, pattern, recursive in src.listings:
        if folder:
            for i in range(len(f) - len(folder)):
                if f[i:i + len(folder)] != folder:
                    continue
                rest = f[i + len(folder):]
                pat = pattern or "*"
                last = _comps(pat)[-1] if _comps(pat) else "*"
                if (recursive or "/" in pat or len(rest) == 1) and (
                        fnmatch.fnmatchcase("/".join(rest), pat) or fnmatch.fnmatchcase(rest[-1], last)):
                    return True
        elif pattern:
            if fnmatch.fnmatchcase(joined, pattern) or fnmatch.fnmatchcase(joined, "*/" + pattern):
                return True
        else:
            for lit in src.literals:
                if any(lit == f[:k] for k in range(1, len(f))):
                    return True
    return False


class Graph:
    def __init__(self, root: Path, extra_paths: set[str] = frozenset()):
        self.root = root
        files = set()
        for d in SOURCE_DIRS:
            base = root / d
            if base.is_dir():
                files |= {p.relative_to(root).as_posix() for p in base.rglob("*.py")}
        files |= {p.name for p in root.glob("*.py")}
        self.files = files
        known = files | {_norm(p) for p in extra_paths}

        def exists(rel: str) -> bool:
            return rel in known or (root / rel).is_file()

        self.sources = {rel: parse_source(root, rel, exists) for rel in sorted(files)}
        self.tests = sorted(r for r in files if is_test_file(r))

    def affected(self, changed: list[str]) -> set[str]:
        """Every source whose behaviour a change can alter, the changed sources themselves included.

        A file's bytes differ only if it is changed, so a source that *names* or *walks into* a file depends on it only
        when that file is changed. Behaviour propagates further only as code runs: through an import of an affected
        file, or through a name of an affected Python file (a script run as a subprocess, a module loaded by path)."""
        hit = {_norm(c) for c in changed}
        out = {r for r in hit if r in self.sources}
        for rel, s in self.sources.items():               # the direct readers of the changed bytes
            if rel not in out and any(names_file(s, p) or lists_file(s, p) for p in hit):
                out.add(rel)
        frontier = set(out)
        while frontier:                                   # what runs them: importers, and runners of a named script
            new = set()
            py = {f for f in frontier if f.endswith(".py")}
            for rel, s in self.sources.items():
                if rel in out:
                    continue
                if s.imports & frontier or any(names_file(s, f) for f in py):
                    new.add(rel)
            out |= new
            frontier = new
        return out


# ------------------------------------------------------------------------------------------------ the decision

def _expand(root: Path, patterns: tuple[str, ...]) -> list[str]:
    out = []
    for p in patterns:
        out += sorted(x.relative_to(root).as_posix() for x in root.glob(p)) if GLOB_CHARS & set(p) else (
            [p] if (root / p).is_file() else [])
    return out


def preflight_tests(changed: list[str], root: Path = ROOT, direct_max: int = PREFLIGHT_DIRECT_MAX) -> list[str]:
    """The pre-flight's test files (E-274): PREFLIGHT_GUARDS, every staged test file, and -- when there are at most
    `direct_max` of them -- the tests that import or name a staged file directly (one step, not the closure). It only
    refuses early: the tier's own stage runs every test it selects, these included."""
    changed = sorted({_norm(c) for c in changed if c.strip()})
    out = set(_expand(root, PREFLIGHT_GUARDS))
    out |= {c for c in changed if is_test_file(c) and (root / c).is_file()}
    if changed:
        graph = _graph(root, set(changed))
        direct = {rel for rel, s in graph.sources.items() if is_test_file(rel) and (
            s.imports & set(changed) or any(names_file(s, c) or lists_file(s, c) for c in changed))}
        if len(direct) <= direct_max:
            out |= direct
    return sorted(out)


_GRAPH_CACHE: dict = {}


def _graph(root: Path, extra: set[str]) -> "Graph":
    """One Graph per (root, staged paths) in a process: the hook's call builds it once for both outputs."""
    key = (str(root), frozenset(extra))
    if key not in _GRAPH_CACHE:
        _GRAPH_CACHE.clear()
        _GRAPH_CACHE[key] = Graph(root, extra)
    return _GRAPH_CACHE[key]


def decide(changed: list[str], *, main_tree: bool, merging: bool, root: Path = ROOT) -> Decision:
    changed = sorted({_norm(c) for c in changed if c.strip()})
    if merging:
        return Decision("T2", "a merge commit (MERGE_HEAD): the full fast tier")
    if not changed:
        return Decision("T2", "nothing staged: the full fast tier")
    for c in changed:
        why = fallback_reason(c)
        if why:
            return Decision("T2", f"fallback: {why}")
    records = all(is_record(c) for c in changed)
    if not records and main_tree:
        return Decision("T2", "the main tree's code commit: the full fast tier")
    graph = _graph(root, set(changed))
    for c in changed:
        if c in graph.sources and graph.sources[c].error:
            return Decision("T2", f"fallback: {c} does not parse ({graph.sources[c].error})")
    hit = graph.affected(changed)
    tests = {r for r in hit if is_test_file(r)} | {c for c in changed if is_test_file(c) and (root / c).is_file()}
    for c in changed:
        p = PurePosixPath(c)
        if p.parts[:1] == ("tests",) and p.suffix == ".py" and not is_test_file(c) and (root / c).is_file():
            reached = {r for r in graph.affected([c]) if is_test_file(r)}
            if not reached:
                return Decision("T2", f"fallback: {c} is a test helper no test reaches (the graph cannot place it)")
        if any(c.startswith(d) for d in NAMED_OR_FULL) and not any(
                names_file(s, c) or lists_file(s, c) or c in s.imports for s in graph.sources.values()):
            return Decision("T2", f"fallback: {c} is named by no source (the graph cannot place it)")
    if records:
        tests |= set(_expand(root, T0_ALWAYS)) | set(_expand(root, ALWAYS))
        return Decision("T0", f"records only ({len(changed)} path(s)): {len(tests)} test file(s) that read them",
                        sorted(tests))
    tests |= set(_expand(root, ALWAYS))
    if graph.tests and len(tests) > FULL_FRACTION * len(graph.tests):
        return Decision("T2", f"the selection is {len(tests)} of {len(graph.tests)} test files (over "
                              f"{FULL_FRACTION:.0%}): the full, parallel fast tier")
    return Decision("T1", f"a worker's code commit ({len(changed)} path(s)): {len(tests)} of {len(graph.tests)} test "
                          f"file(s)", sorted(tests))


# ------------------------------------------------------------------------------------------------ the hook's call

def _git(root: Path, *args: str, index: str | None = None) -> str:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    if index:
        env["GIT_INDEX_FILE"] = index
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=120, env=env)
    if p.returncode != 0:
        raise SelectionError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def staged(root: Path = ROOT, index: str | None = None) -> list[str]:
    return [ln for ln in _git(root, "diff", "--cached", "--name-only", "--no-renames", index=index).splitlines()
            if ln.strip()]


def merging(root: Path = ROOT) -> bool:
    gitdir = Path(_git(root, "rev-parse", "--absolute-git-dir").strip())
    return (gitdir / "MERGE_HEAD").exists()


def is_main(root: Path = ROOT) -> bool:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fasttier_lock import is_main_worktree
    return is_main_worktree(root)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hook", action="store_true", help="print the tier and its reason; write the selection to --out")
    ap.add_argument("--explain", action="store_true", help="print the decision and the selected files")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--index", default=None, help="the index the commit records (the hook's GIT_INDEX_FILE)")
    ap.add_argument("--preflight-out", type=Path, default=None,
                    help="write the pre-flight's test files (the always-on guards and the nearest tests) here")
    a = ap.parse_args(argv)
    changed: list[str] = []
    try:
        changed = staged(ROOT, a.index)
        d = decide(changed, main_tree=is_main(ROOT), merging=merging(ROOT))
    except Exception as e:                                # noqa: BLE001 -- any failure: the full tier, said
        d = Decision("T2", f"fallback: the selector failed ({type(e).__name__}: {e})")
    if a.out is not None:
        a.out.write_text("".join(f"{t}\n" for t in d.tests), encoding="utf-8")
    if a.preflight_out is not None:
        try:
            pre = preflight_tests(changed, ROOT)
        except Exception:                                 # noqa: BLE001 -- the guards alone, never nothing
            pre = _expand(ROOT, PREFLIGHT_GUARDS)
        a.preflight_out.write_text("".join(f"{t}\n" for t in pre), encoding="utf-8")
    print(d.tier)
    print(d.reason)
    if a.explain:
        for t in d.tests:
            print(f"  {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
