"""The pre-commit hook's pre-flight (Q-209 as reworked by the lead's ruling on the red team's BLOCK; E-274).

    python scripts/fasttier_preflight.py --explain                # what the staged change's pre-flight would run
    python scripts/fasttier_preflight.py --out <file> --index <i> # the hook's call: the test files, one per line

**What it is.** The first stage of the commit's fast tier, inside the same slot of the fast-tier lock and through the
same runner (`scripts/fasttier_xdist.py --preflight <file>`): a short serial pytest over

1. PREFLIGHT_GUARDS -- E-274's always-on guards (the heavy-marker and heavy guards, the seed guard, the identity tokens,
   the declarations, the git scan, the trace check, vendor integrity, reader*);
2. every staged test file;
3. the tests that import, or name, or list (a folder listing bound to its call) a staged file directly -- one step,
   not a closure -- when there are at most PREFLIGHT_DIRECT_MAX of them.

A failure refuses the commit there, minutes into its slot, before the full fast tier starts; a refused commit no longer
holds the shared line for a full run. **It selects nothing away**: the full fast tier (every test not slow and not
heavy) runs after it on every commit, main tree and worker trees alike, so an incomplete pre-flight costs only an early
refusal it missed. (The lead's ruling dropped test selection -- the T0 and T1 tiers -- after the red team showed a
records-only selection skipping failing tests and master's code states left without a full run.)

**The direct tests** come from a static read of every Python file under tests/, extended/, scripts/ and identity/:
imports (`import a.b`, `from a import b`, relative imports, `importlib.import_module("x")`, bare names as the suite's
sys.path inserts resolve them, each package's `__init__.py` on the way); names (a string literal, or a `/` chain,
`Path(...)` or `os.path.join(...)` of literals, holding the file's path or its file name as a path component, or its
dotted module name); and folder listings bound to their own call (`path.glob(p)`, `path.rglob(p)`, `path.iterdir()`,
`os.listdir/scandir/walk(folder)`, `glob.glob(p)`, `fnmatch.*(name, p)` with a constant pattern; the folder is the
receiver's constant parts, an f-string pattern reads each formatted part as `*`). A walk of a folder it cannot name, of
every file, is no *direct* dependency (it would name every test), and the full tier covers it.
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

#: E-274's always-on guards
PREFLIGHT_GUARDS = ("tests/test_heavy_marker_guard.py", "tests/test_heavy_guard.py", "tests/test_seed_derivation_guard.py",
                    "tests/test_identity_tokens.py", "tests/test_declarations_fixed.py", "tests/test_git_scan.py",
                    "tests/test_trace_check.py", "tests/test_vendor_integrity.py", "tests/test_reader*.py")
#: the direct tests join the pre-flight only when there are at most this many (it stays a minutes-long stage)
PREFLIGHT_DIRECT_MAX = 10
SOURCE_DIRS = ("tests", "extended", "scripts", "identity")
BARE_DIRS = ("scripts", "tests", "identity", "scripts/hooks", "")
LIST_METHODS = ("iterdir", "glob", "rglob")                  # path.<m>(pattern): the receiver is the folder
MATCH_FUNCS = ("fnmatch", "fnmatchcase", "filter")             # fnmatch.<f>(name, pattern)
GLOB_CHARS = set("*?[")
EVERYTHING = (None, "*", "**", "**/*")                         # a pattern that bounds nothing


@dataclass
class Source:
    rel: str
    imports: set[str] = field(default_factory=set)      # repository files it imports (resolved)
    literals: list[tuple[str, ...]] = field(default_factory=list)   # path-like literals, as components
    raw: set[str] = field(default_factory=set)          # every string literal, normalised
    #: its folder listings: (the folder's constant components or None if unknown, the pattern or None, recursive)
    listings: list = field(default_factory=list)
    error: str | None = None


# ------------------------------------------------------------------------------------------------ paths

def _norm(s: str) -> str:
    s = s.replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return s


def _comps(s: str) -> tuple[str, ...]:
    return tuple(c for c in _norm(s).split("/") if c and c != ".")


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

def _call_name(node: ast.Call) -> str:
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""


def _joined(node: ast.AST) -> str | None:
    """The string a `/` chain, `Path(...)` or `os.path.join(...)` of string constants spells, constants only."""
    parts: list[str] = []

    def walk(n) -> None:
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            parts.append(n.value)
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            walk(n.left)
            walk(n.right)

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        walk(node)
    elif isinstance(node, ast.Call) and _call_name(node) in ("Path", "PurePath", "PurePosixPath", "join"):
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
        tree = ast.parse((root / rel).read_text(encoding="utf-8", errors="replace"), filename=rel)
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
                    s.imports |= _resolve(f"{mod}.{a.name}", rel, exists)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            s.raw.add(_norm(node.value))
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
                    s.listings.append(listing)
    s.literals = [c for c in (_comps(v) for v in s.raw) if c]
    return s


# ------------------------------------------------------------------------------------------------ direct edges

def _contiguous(needle: tuple[str, ...], hay: tuple[str, ...]) -> bool:
    n = len(needle)
    return n > 0 and any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def names_file(src: Source, path: str) -> bool:
    """Whether `src` names `path`: a literal holding its path or its file name as a path component, or its dotted
    module name (`-m extended.x`). A bare stem is no name (as a literal it is a word: "status")."""
    f = _comps(path)
    if not f:
        return False
    if any(_contiguous(f, lit) or f[-1] in lit for lit in src.literals):
        return True
    return bool({m for m in module_names(path) if "." in m} & src.raw)


def lists_file(src: Source, path: str) -> bool:
    """Whether one of `src`'s bound folder listings can see `path`: its folder occurs among the path's folders and the
    rest matches its pattern (a non-recursive listing sees only the folder's own files); with no folder known, its
    pattern matches the path. A walk that bounds nothing is no direct edge."""
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
        elif pattern not in EVERYTHING:
            if fnmatch.fnmatchcase(joined, pattern) or fnmatch.fnmatchcase(joined, "*/" + pattern):
                return True
    return False


class Graph:
    def __init__(self, root: Path, extra_paths: set[str] = frozenset()):
        files = set()
        for d in SOURCE_DIRS:
            base = root / d
            if base.is_dir():
                files |= {p.relative_to(root).as_posix() for p in base.rglob("*.py")}
        files |= {p.name for p in root.glob("*.py")}
        known = files | {_norm(p) for p in extra_paths}

        def exists(rel: str) -> bool:
            return rel in known or (root / rel).is_file()

        self.sources = {rel: parse_source(root, rel, exists) for rel in sorted(files)}

    def direct_tests(self, changed: list[str]) -> set[str]:
        """The test files that import, name or list a changed path directly (one step)."""
        hit = {_norm(c) for c in changed}
        return {rel for rel, s in self.sources.items() if is_test_file(rel) and (
            s.imports & hit or any(names_file(s, c) or lists_file(s, c) for c in hit))}


# ------------------------------------------------------------------------------------------------ the pre-flight

def _expand(root: Path, patterns: tuple[str, ...]) -> list[str]:
    out = []
    for p in patterns:
        out += sorted(x.relative_to(root).as_posix() for x in root.glob(p)) if GLOB_CHARS & set(p) else (
            [p] if (root / p).is_file() else [])
    return out


def preflight_tests(changed: list[str], root: Path = ROOT, direct_max: int = PREFLIGHT_DIRECT_MAX) -> list[str]:
    """PREFLIGHT_GUARDS, every staged test file, and -- when there are at most `direct_max` of them -- the tests that
    import, name or list a staged file directly."""
    changed = sorted({_norm(c) for c in changed if c.strip()})
    out = set(_expand(root, PREFLIGHT_GUARDS))
    out |= {c for c in changed if is_test_file(c) and (root / c).is_file()}
    if changed:
        direct = Graph(root, set(changed)).direct_tests(changed)
        if len(direct) <= direct_max:
            out |= direct
    return sorted(out)


def staged(root: Path = ROOT, index: str | None = None) -> list[str]:
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}
    if index:
        env["GIT_INDEX_FILE"] = index
    p = subprocess.run(["git", "diff", "--cached", "--name-only", "--no-renames"], cwd=root, capture_output=True,
                       text=True, timeout=120, env=env)
    if p.returncode != 0:
        raise RuntimeError(f"git diff --cached: {p.stderr.strip()}")
    return [ln for ln in p.stdout.splitlines() if ln.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None, help="write the pre-flight's test files here, one per line")
    ap.add_argument("--index", default=None, help="the index the commit records (the hook's GIT_INDEX_FILE)")
    ap.add_argument("--explain", action="store_true")
    a = ap.parse_args(argv)
    try:
        tests = preflight_tests(staged(ROOT, a.index or None), ROOT)
    except Exception as e:                                # noqa: BLE001 -- the guards alone, said; never nothing
        print(f"pre-flight: the direct tests could not be read ({type(e).__name__}: {e}); the guards alone",
              file=sys.stderr)
        tests = _expand(ROOT, PREFLIGHT_GUARDS)
    if a.out is not None:
        a.out.write_text("".join(f"{t}\n" for t in tests), encoding="utf-8")
    if a.explain or a.out is None:
        for t in tests:
            print(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
