"""H4's draft declaration (`prereg/DRAFT_H4_rebaseline.md`), its T-0: checked on its own text, on its plan script, on
W42-R1's code at its commit and on the repository's files (no engine, no bar, no result file; fast). Second text:
corrective cycle 1 answers the red team's read (`H4_DECL_2026-11-20`), whose surviving mutants each have a killing test
here (m-1).

- **the form** -- `prereg/TEMPLATE_family.md`'s sections 0 to 19 and four appendices, in order, read as LF text; a
  described reading that takes **no k**; the form's choice stated (the family form, the design-search template v2
  wherever it governs: its section 5 and its section 14's held-out line);
- **the seed table** -- section 15 lists the ten consecutive seeds of H4's block once each, three roles and seven
  spares; no other eight-digit 2026 token in the text; no tracked or working file of any suffix but this draft, the
  seed module and H4's own result manifests carries a literal of the block; the arithmetic fold over every tracked
  `.py` -- the three-way design test's folder and this file's widened evaluator (strings, f-strings, `int()`, numpy
  integers, `sum`; m-7) -- finds the block's construction only in this file and the seed module; planted controls;
- **no typed figure** -- outside the script's fenced output, identifier and path code spans, the seed rows, dates,
  times, ids, hashes and section, measure and list references, every number is one of a short list with its source,
  and no number word is spelled out (planted figures, in each of the red team's forms, are caught);
- **no held-out window** -- no judged-block reads line at all (v2's section 14), every date after the search years a
  declared bound in an unread sentence, the refusal bounds' sentences held exactly, the plan on search-year sessions;
- **the rulings carried** -- the strict rule and the overlap count (B-1), the pass-through constants and the sub-hash
  (B-2), the point arm (B-3), the one collection result, uncapped sessions left and the required keys (B-4), I-5 (B-5),
  J refused until W42-R1's pin (B-6), the held-out read ledger (B-7), the minors, and v2's section 5;
- **the dependencies named** -- Appendix C, each with where, its status and what H4 needs; the cited commits and files
  exist; the built ones hold the names H4 uses;
- **the measures and W42-R1's inputs** -- every measure of `docs/MEASURES.md`'s index placed in Appendix B; every key of
  W42-R1's `REQUIRED` named, the three workload and supply measures among them; MEASURES (35) amended (m-6);
- **cycle 2** -- RB-1 (the coin's unchained offers, its schedule-side seed, the vendored routing, I-5 by `trades_hash`),
  RB-2 (the per-unit overlap count on the taken-trade log, recomputed by the auditor), W42-R1 at 34ee968 (rm-1), the
  surviving mutants' sentences (rm-2, E1 to E28), the ledger (rm-3), the constants copied (rm-4), the jobs through the
  cut (rm-5), the calendar against the cut (rm-6), the scratch git-ignored (rn-1), v3 (rn-2), the look-ahead (rn-3),
  the as-walked exit times (rn-4); Appendix E maps them;
- **the plan is the script's** -- Appendix A equals `docs/plans/scripts/h4/h4_plan.py`'s output line for line; its
  figures (J, the gaps, the work) recomputed here from the formulas; its constants equal W42-R1's at the provisional
  commit (or the pinned one), `family_stats.MDL_POWER` and `user_beside.EXACT_EVERY`.
"""
from __future__ import annotations

import ast
import importlib.util
import math
import re
import subprocess
import sys
import types
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "prereg" / "DRAFT_H4_rebaseline.md"
TEMPLATE = ROOT / "prereg" / "TEMPLATE_family.md"
TEMPLATE_V2 = ROOT / "prereg" / "TEMPLATE_design_search.md"
PLAN = ROOT / "docs" / "plans" / "scripts" / "h4" / "h4_plan.py"
MEASURES = ROOT / "docs" / "MEASURES.md"
THREE_WAY_TEST = ROOT / "tests" / "test_three_way_design.py"
VENDOR_DATA = ROOT / "vendor" / "stage2" / "data"
THIS = Path(__file__).resolve().relative_to(ROOT).as_posix()

#: section 15's block, built by arithmetic so that this file holds no literal of it
_PREFIX = 2026 * 1000 + 440
H4_BLOCK = tuple(_PREFIX * 10 + i for i in range(10))
#: the files allowed to hold a literal of the block: this draft, the seed module once it is given the block, and H4's
#: own result manifests (a manifest records its seeds)
DECLARED_USES = ("prereg/DRAFT_H4_rebaseline.md", "extended/three_way_seeds.py")
#: H4's declared result files (section 16's outputs): only their sidecar manifests, whose seed maps record the block
_B = r"(naive_coin|p14|p15|p16)"
DECLARED_PATTERNS = (re.compile(rf"^results/h4_(units_{_B}|readings_{_B}|trades_{_B}|w42_input|supply|as_traded|identities)"
                                r"\.csv\.manifest\.json$"),)
#: the files allowed to construct it by arithmetic: this test, and the seed module
DERIVED_USES = (THIS, "extended/three_way_seeds.py")
#: the commit whose W42-R1 constants the provisional J reads, and the runner's
PROVISIONAL_W42, RUNNER_COMMIT = "c014d0a", "adedf7f"
SKIP_DIRS = {".git", "data", "__pycache__", ".pytest_cache", "node_modules"}
W42_PLACEHOLDER = "`<W42-R1's pinning row and the LF sha256 of its three files, filled at W42-R1's pin>`"
NESTED_CUTS = ("2022-12-30", "2023-06-30", "2023-09-29")

#: the numbers the text may hold outside the stripped forms, each a declared value or a rule cited by its source
ALLOWED_NUMBERS = {
    **{str(d): "a single digit: a list item, a count in a sentence, a tick or a worker count" for d in range(10)},
    "10": "measure (28)'s 10 % of signals missed (CHARTER 3.8 (c)); D-212's 10 % realised-risk band",
    "20": "measure (28)'s other level, 20 %, named as not read",
    "21": "a month is 21 sessions (CHARTER 2); measures (4) and (8) at session 21; a batch of a month of starts",
    "63": "months 1-3, P_B's horizon (MEASURES section 2)",
    "90": "D-212's 90 % of trades (CHARTER section 4)",
    "126": "W, W42-R1's window (U1's and Q-44's ledger constant)",
    "252": "twelve months, the observation window's cap (MEASURES 1.1)",
    "2020": "the search years' first calendar year (E-208)",
    "2023": "the search years' last calendar year (E-208)",
    "2024": "the held-out years' first calendar year, named as unread",
    "2026": "the held-out years' last calendar year, named as unread",
}
#: number words a figure could be spelled in (m-1, D17); the small counts the text uses in words are not listed
NUMBER_WORDS = re.compile(r"\b(eleven|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|"
                          r"forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|percent|"
                          r"per cent)\b", re.IGNORECASE)
HELD_DATES = {"2024-01-02": "the held-out years' first day", "2026-07-16": "the held-out years' last day",
              "2026-07-17": "the confirmation window's first day"}
#: dates from here on are the record's (this program's documents, from its start in 2026-11), never a market session:
#: the development bars end 2026-07-16
RECORD_DATES_FROM = "2026-11-01"
UNREAD_WORDS = ("never read", "refus", "unread", "held-out years", "confirmation window", "held-out read", "is excluded")
FINDINGS = tuple(f"B-{i}" for i in range(1, 8)) + tuple(f"m-{i}" for i in range(1, 8))
FINDINGS_C2 = ("RB-1", "RB-2") + tuple(f"rm-{i}" for i in range(1, 7)) + tuple(f"rn-{i}" for i in range(1, 5))
FINDINGS_C3 = ("RC-1", "RC-2") + tuple(f"rc-{i}" for i in range(3, 14)) + ("rn-a to rn-e",)


def _lf(p: Path) -> str:
    return p.read_bytes().decode("utf-8").replace("\r\n", "\n")


def _flat(s: str) -> str:
    return " ".join(s.split())


@pytest.fixture(scope="module")
def text() -> str:
    return _lf(DRAFT)


def _between(t: str, start: str, end: str) -> str:
    i, j = t.index(start), t.index(end)
    return t[i + len(start):j]


def _section(t: str, n: int) -> str:
    return t[t.index(f"\n## {n}. "):t.index(f"\n## {n + 1}. ") if n < 19 else t.index("\n## Appendix A. ")]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def plan():
    return _load(PLAN, "h4_plan_for_t0")


def _git(*args: str, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


def _show(commit: str, path: str) -> str:
    return _git("show", f"{commit}:{path}").stdout


@pytest.fixture(scope="module")
def w42(plan):
    """W42-R1's module at the pinned commit (once `W42_PIN` is set) or the provisional one, executed from its source
    (pure: it imports numpy and `family_stats` only)."""
    commit = plan.W42_PIN["commit"] if plan.W42_PIN is not None else PROVISIONAL_W42
    name = f"wave42_at_{commit}_for_h4"
    mod = types.ModuleType(name)
    sys.modules[name] = mod                      # its dataclasses look their module up there
    try:
        exec(compile(_show(commit, "extended/wave42.py"), name, "exec"), mod.__dict__)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return mod


# ------------------------------------------------------------------------------------------------------- the form


def test_the_form(text: str) -> None:
    assert text.startswith("# H4: ")
    assert "**Status: a draft, text 4 -- a re-declaration, for the red team's full read, with its own two corrective " \
        "cycles.**" in _flat(text)
    assert "Under the failure protocol this text is a new declaration" in _flat(text)
    assert "`prereg/TEMPLATE_family.md`'s form\n(sections 0 to 19)" in text
    heads = [f"\n## {n}. " for n in range(20)] + [f"\n## Appendix {a}. " for a in "ABCDEF"]
    pos = [text.find(h) for h in heads]
    assert all(p >= 0 for p in pos), [h for h, p in zip(heads, pos) if p < 0]
    assert pos == sorted(pos)
    assert all(f"\n## {n}. " in _lf(TEMPLATE) for n in range(20)), "the template's sections are 0 to 19"


def test_the_forms_choice_is_stated(text: str) -> None:
    """The lead's ruling on the template's scope: the family form; v2 wherever it governs (its 5 and 14)."""
    flat = _flat(text)
    assert "**Which form, and why**" in flat
    assert "(`prereg/TEMPLATE_design_search.md` v2, wt/wt-lit 68436c9, E-247)" in flat
    assert "its section 5 (the race, L_fill, R-10's stopped walk and its exit map, m-2 and m-3)" in flat
    assert "its section 14's held-out line" in flat
    v2 = _lf(TEMPLATE_V2)
    assert "**Text v2 (2026-11-20).**" in v2
    assert "**There is no \"not taken\" state:**" in v2 and "fractional, never rounded" in v2
    assert "**This search carries no `Judged-block reads:` line" in v2


def test_it_takes_no_k(text: str) -> None:
    flat = _flat(text)
    assert "takes **no k**" in flat and "**H4 takes no k**" in flat
    assert "CHARTER 3.7: one k per held-out test" in flat
    assert "**k:** the next free program family number" in _lf(TEMPLATE)
    assert "**k:**" not in text and "k_cells" not in text
    assert not re.search(r"\bk\s*=\s*\d", text), "no k value is assigned"


# --------------------------------------------------------------------------------------------------- the seeds


def test_the_seed_table(text: str) -> None:
    sec = _section(text, 15)
    rows = re.findall(r"^\| (\d{8}) \| ([^|]+) \| ([^|]+) \|$", sec, re.MULTILINE)
    assert [int(r[0]) for r in rows] == list(H4_BLOCK), "ten consecutive seeds, once each, in order"
    roles = [r[1].strip() for r in rows]
    status = [r[2].strip() for r in rows]
    assert status[:5] == ["tests", "design check", "reading", "schedule", "audit sample"]
    assert roles[5:] == ["spare"] * 5 and status[5:] == ["spare, drawn by nothing"] * 5
    assert len(set(roles[:5])) == 5, "one role each"
    assert roles[4].startswith("`h4b_audit_sample` (the spare `h4_spare_4`, to register): H4-B, the audit sample of "
                               "units -- one draw a unit (start, seed index)")                              # rc-3
    assert "a unit sampled when its draw is below 1 % (section 7)" in roles[4]
    assert roles[3].startswith("`h4s_schedule_side`: H4-S, the coin's schedule side -- one draw a (session, moment)")
    assert "so independent of every seed index" in roles[3]
    toks = set(re.findall(r"\b2026\d{4}\b", text))
    assert toks <= {str(s) for s in H4_BLOCK}, f"another block's seed in the text: {sorted(toks - set(map(str, H4_BLOCK)))}"
    assert not re.search(r"\b2026587\d\b", text), "H3's block is named by role only"
    flat = _flat(sec)
    assert "never the seed plus an offset (E-171)" in flat
    assert ('`PARTS["H4-0"] == 10`, `PARTS["H4-B"] == 11`, `PARTS["H4-T"] == 12` (H4\'s tests) and '
            '`PARTS["H4-S"] == 13`') in flat
    assert "**The audit sample's seed takes the spare `h4_spare_4`** and is named here `h4b_audit_sample`" in flat
    assert "**The scans are a guard, not the defence** (m-7)" in flat and "`ProvenanceRefused`" in flat


_BLOCK_RE = r"\b(" + "|".join(str(s) for s in range(_PREFIX * 10, _PREFIX * 10 + 10)) + r")\b"
_BLOCK_BYTES = re.compile(_BLOCK_RE.encode("ascii"))


def _allowed(rel: str) -> bool:
    return rel in DECLARED_USES or any(p.match(rel) for p in DECLARED_PATTERNS)


def _git_hits(repo: Path) -> set[str]:
    out = _git("grep", "-IlwE", _BLOCK_RE, cwd=repo, check=False).stdout
    return {line.strip() for line in out.splitlines() if line.strip()}


def _file_hit(p: Path, chunk: int = 1 << 24) -> bool:
    """A literal of the block anywhere in the file, read in overlapping chunks; a binary file (a NUL byte in its first
    8 KB) is skipped."""
    with p.open("rb") as fh:
        head = fh.read(8192)
        if b"\0" in head:
            return False
        tail = b""
        buf = head
        while True:
            if _BLOCK_BYTES.search(tail + buf):
                return True
            tail = (tail + buf)[-16:]
            buf = fh.read(chunk)
            if not buf:
                return False


def _working_hits(base: Path) -> set[str]:
    """Every file git can commit (m-7, rn-1): tracked, and untracked files not git-ignored, of any suffix -- a git-ignored
    file (the worker's scratch `.h4_dev/`, the licensed data) cannot be staged by any `git add`; binaries skipped."""
    out = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard", cwd=base).stdout
    found = set()
    for rel_s in sorted({r for r in out.split("\0") if r}):
        p = base / rel_s
        rel = Path(rel_s)
        if not p.is_file() or SKIP_DIRS & set(rel.parts[:-1]) or VENDOR_DATA in p.parents:
            continue
        try:
            if _file_hit(p):
                found.add(rel.as_posix())
        except OSError:
            continue
    return found


def test_the_block_nowhere_else_tracked() -> None:
    hits = _git_hits(ROOT)
    assert all(_allowed(h) for h in hits), f"a literal of H4's block outside its declared uses: {sorted(hits)}"


def test_the_block_nowhere_else_working() -> None:
    hits = _working_hits(ROOT)
    assert "prereg/DRAFT_H4_rebaseline.md" in hits, "the scan must find the draft's own table (positive control)"
    assert all(_allowed(h) for h in hits), f"a literal of H4's block outside its declared uses: {sorted(hits)}"


def test_the_scans_find_a_planted_seed(tmp_path: Path) -> None:
    _git("init", "-q", cwd=tmp_path)
    (tmp_path / "x.md").write_text(f"a seed {H4_BLOCK[7]} here\n", encoding="utf-8")
    (tmp_path / "y.txt").write_text(f"not a seed: {H4_BLOCK[7]}1 nor 1{H4_BLOCK[7]}\n", encoding="utf-8")
    (tmp_path / "run.log").write_text(f"an untracked log naming {H4_BLOCK[4]}\n", encoding="utf-8")   # any suffix
    (tmp_path / "blob.bin").write_bytes(b"\0" + str(H4_BLOCK[4]).encode())                          # a binary, skipped
    (tmp_path / ".gitignore").write_text("scratch/\n", encoding="utf-8")
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "backup.md").write_text(f"ignored {H4_BLOCK[2]}\n", encoding="utf-8")  # git-ignored
    _git("add", "x.md", "y.txt", cwd=tmp_path)
    assert _git_hits(tmp_path) == {"x.md"}
    assert _working_hits(tmp_path) == {"x.md", "run.log"}


@pytest.fixture(scope="module")
def folder():
    """The three-way design test's arithmetic folder (pure-literal expressions, names, `**`, tuple unpacking and
    augmented assignment; its N-9), loaded from that file, never copied."""
    return _load(THREE_WAY_TEST, "three_way_design_folder_for_h4")._Folder


_LIMIT = 10 ** 15
_INT_CALLS = {"int", "int64", "int32", "uint64", "uint32", "int_", "intc", "longlong"}


def _value(node: ast.AST, env: dict):
    """m-7's widened evaluator: an int, a str or a list of them, from literals, bound names, arithmetic, string
    concatenation, f-strings, `int()` and numpy integer calls and `sum` of literals; None otherwise."""
    if isinstance(node, ast.Constant) and type(node.value) in (int, str):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _value(node.operand, env)
        return -v if type(v) is int else None
    if isinstance(node, (ast.List, ast.Tuple)):
        vals = [_value(e, env) for e in node.elts]
        return vals if all(v is not None for v in vals) else None
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            elif isinstance(v, ast.FormattedValue) and v.format_spec is None and v.conversion == -1:
                x = _value(v.value, env)
                if type(x) not in (int, str):
                    return None
                parts.append(str(x))
            else:
                return None
        return "".join(parts)
    if isinstance(node, ast.BinOp):
        a, b = _value(node.left, env), _value(node.right, env)
        if type(a) is str and type(b) is str and isinstance(node.op, ast.Add):
            return a + b
        if type(a) is not int or type(b) is not int or abs(a) > _LIMIT or abs(b) > _LIMIT:
            return None
        try:
            if isinstance(node.op, ast.Add):
                v = a + b
            elif isinstance(node.op, ast.Sub):
                v = a - b
            elif isinstance(node.op, ast.Mult):
                v = a * b
            elif isinstance(node.op, ast.FloorDiv):
                v = a // b
            elif isinstance(node.op, ast.Mod):
                v = a % b
            elif isinstance(node.op, ast.Pow) and 0 <= b <= 64:
                v = a ** b
            else:
                return None
        except ZeroDivisionError:
            return None
        return v if abs(v) <= _LIMIT else None
    if isinstance(node, ast.Call) and len(node.args) == 1 and not node.keywords:
        f = node.func
        fname = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
        x = _value(node.args[0], env)
        if fname in _INT_CALLS:
            if type(x) is int:
                return x
            if type(x) is str and x.strip().lstrip("-").isdigit() and len(x.strip()) <= 16:
                return int(x)
        if fname == "sum" and isinstance(x, list) and all(type(v) is int for v in x):
            return sum(x)
    return None


class _Widened(ast.NodeVisitor):
    """Binds plain names in source order and records every expression whose value is a target."""

    def __init__(self, targets: set[int]):
        self.targets, self.env, self.lines = targets, {}, []

    def _hit(self, v, line: int) -> None:
        if type(v) is int and v in self.targets:
            self.lines.append(line)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.generic_visit(node)
        v = _value(node.value, self.env)
        for t in node.targets:
            if isinstance(t, ast.Name):
                if v is None:
                    self.env.pop(t.id, None)
                else:
                    self.env[t.id] = v

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, ast.expr):
            self._hit(_value(node, self.env), getattr(node, "lineno", 0))
        super().generic_visit(node)


def _fold_hits(folder, source: str) -> list[int]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source)
    except SyntaxError:
        return []
    targets = {_PREFIX, _PREFIX * 10, *H4_BLOCK}
    f = folder(targets)
    f.visit(tree)
    w = _Widened(targets)
    w.visit(tree)
    return sorted(set(f.lines) | set(w.lines))


def test_the_fold_finds_the_construction_only_where_declared(folder) -> None:
    files = _git("ls-files", "*.py").stdout.splitlines()
    found = set()
    for f in files:
        p = ROOT / f
        if p.is_file() and VENDOR_DATA not in p.parents and _fold_hits(folder, p.read_text("utf-8", errors="replace")):
            found.add(f)
    if _git("ls-files", THIS).stdout.strip():
        assert THIS in found, "the fold must find this file's own construction of the block (positive control)"
    assert found <= set(DERIVED_USES), f"H4's block is built by arithmetic outside its declared uses: {found}"


@pytest.mark.parametrize("src", [
    "Y = 2 ** 11 - 22\nP = Y * 1000 + 440\nS = P * 10 + 2\n",
    'S = int("2026440" + "2")\n',
    'S = int(f"{2026440}2")\n',
    "S = sum([20264000, 402])\n",
    "import numpy as np\nS = np.int64(2026440) * 10 + 2\n",
    f"B = {H4_BLOCK[0]}\nS = B + 2\n",
])
def test_the_fold_sees_a_planted_construction(folder, src: str) -> None:
    """The three-way folder's form and every construction the red team's m-7 found unseen."""
    assert _fold_hits(folder, src), src


def test_the_fold_ignores_a_near_miss(folder) -> None:
    assert _fold_hits(folder, "Q = 2026 * 1000 + 441\nR = int('2026441' + '2')\nT = 'P = 2026 * 1000 + 440'\n") == []


# --------------------------------------------------------------------------------------------- no typed figure


def _code_span(m: re.Match) -> str:
    """An identifier or path span is dropped; a span that starts with a digit keeps its content for the scan (m-1)."""
    body = m.group(1)
    return f" {body} " if body[:1].isdigit() or body[:1] in "+-." else " "


def _stripped(t: str) -> str:
    """The text less what may hold a number: the script's fenced output, Appendix B's and D's tables (their numbers are
    MEASURES' and the findings' ids; Appendix B's horizons are checked apart), identifier and path code spans, the seed
    rows, dates, clock times, ids (E-208, P-14, H3-D, W42-R1, RD-04 ...), short codes (H4, S1, T4, U1), hashes, measure
    references in their one form ("measure (N)", "measures (N) and (M)", "MEASURES (N)"), section numbers and the key
    words' bound."""
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    for a, b in (("<!-- h4_measures: begin -->", "<!-- h4_measures: end -->"),
                 ("<!-- h4_findings: begin -->", "<!-- h4_findings: end -->"),
                 ("<!-- h4_findings_c2: begin -->", "<!-- h4_findings_c2: end -->"),
                 ("<!-- h4_findings_c3: begin -->", "<!-- h4_findings_c3: end -->")):
        t = t.replace(_between(t, a, b), " ")
    t = re.sub(r"`([^`\n]*)`", _code_span, t)
    t = re.sub(r"^\| \d{8} \|.*$", " ", t, flags=re.M)
    t = re.sub(r"\b(?:CHARTER|MEASURES|Wave|note|note's|its|W42-R1|sections?)\s+[1-9]\.\d{1,2}\b", " ", t)
    t = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", t)
    t = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", " ", t)
    t = re.sub(r"\b[A-Za-z]{1,4}\d*-\d+[A-Za-z]?\b", " ", t)
    t = re.sub(r"\b[A-Z]{1,2}\d{1,2}\b", " ", t)
    t = re.sub(r"\b[0-9a-f]{7,64}\b", " ", t)
    t = re.sub(r"\b(?:measures?|MEASURES)\s+\(\d{1,2}\)(?:(?:,|\s+and|\s+to|\s+or|,\s+and|\s+/)\s*\(\d{1,2}\))*", " ", t)
    t = re.sub(r"\b(?:sections?|Appendix)\s+\d{1,2}(?:\.\d{1,2})?(?:\s+(?:to|or|and)\s+\d{1,2})?\b", " ", t)
    t = re.sub(r"\b2\^\d{1,2}\b", " ", t)
    t = re.sub(r"^## \d{1,2}\. ", " ", t, flags=re.M)
    return t


def _numbers(t: str) -> set[str]:
    return set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])", _stripped(t)))


def _typed(t: str) -> set[str]:
    words = {w.lower() for w in NUMBER_WORDS.findall(_stripped(t))}
    return (_numbers(t) - set(ALLOWED_NUMBERS)) | words


def test_no_typed_figure(text: str) -> None:
    extra = _typed(text)
    assert not extra, f"numbers typed outside the declared list (compute them in the script): {sorted(extra)}"


@pytest.mark.parametrize("plant", ["the coin seeds are J = 128 here", "a gap of 0.0092 resolved",
                                   "the cap is 2.5 GB", "a gap of `0.0092` resolved", "its 87 % resolved",
                                   "the coin trades (12) a day", "eighty-seven percent resolved"])
def test_no_typed_figure_catches_a_planted_one(text: str, plant: str) -> None:
    """The red team's D8, D9, D16 and D17 forms among them."""
    planted = text.replace("## 10. Power before the pin: J", f"## 10. Power before the pin: J\n\n{plant}")
    assert _typed(planted), plant


def test_every_figure_of_the_plan_is_in_the_scripts_block(text: str, plan) -> None:
    outside = re.sub(r"```.*?```", " ", text, flags=re.S)
    for v in (plan.j_provisional(), plan.j_needed(), plan.units_needed(), plan.sessions_upper(), plan.sessions_lower()):
        assert not re.search(rf"(?<![\w.]){v}(?![\w])", outside), v


# ------------------------------------------------------------------------------------------- no held-out window


def test_no_held_out_window(text: str, plan) -> None:
    from extended import reader

    assert reader.declared_purposes(text) == frozenset(), "no held-out purpose"
    assert not reader.DECLARED_LINE.search(text), "no judged-block reads line at all (v2's section 14)"
    assert "**H4 carries no judged-block reads line**" in _section(text, 13)
    for line in text.splitlines():
        for d in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", line):
            if d >= RECORD_DATES_FROM:
                continue
            if d > "2023-12-29":
                assert d in HELD_DATES, f"a date after the search years that is no declared bound: {d}"
                assert any(w in line for w in UNREAD_WORDS) or line.startswith("| never read"), line
    assert plan.A.SEARCH == ("2020-01-02", "2023-12-29")
    assert not re.search(r"\b202[4-9]-\d{2}-\d{2}\b", plan.report()), "the plan counts search-year sessions only"


def test_the_refusal_bounds_are_held_exactly(text: str) -> None:
    """D1, D2: the reader's and the runner's refusal bound is the held-out years' first day."""
    flat = _flat(text)
    assert "Any read whose span reaches 2024-01-02 is refused by the reader before it opens a file." in flat
    assert ("the runner's `Plan` refuses any unit whose window holds a session from 2024-01-02 (`HeldOutRefused`; "
            "CHARTER 3.6 (e))") in flat
    assert "refusing any session from 2024-01-02" in flat and "refusing any span reaching 2024-01-02" in flat
    for m in re.finditer(r"[^.]*\brefus[^.]*\b(\d{4}-\d{2}-\d{2})\b[^.]*", flat):
        assert m.group(1) in ("2024-01-02", "2023-12-29") or m.group(1) >= RECORD_DATES_FROM, m.group(0)


def test_the_refusals_and_kills_are_held_exactly(text: str) -> None:
    """D3, D5, D11, D12, D15: each refusal, the failure rule, the nested check's kill, the oracle as a floor."""
    s16, s14, s11, s9 = (_flat(_section(text, n)) for n in (16, 14, 11, 9))
    first = s16[s16.index("1. **Refusals first**"):s16.index("2. **H4-0**")]
    assert "**W42-R1 pinned before H4 is read** (CHARTER 3.9; E-221)" in first
    assert "this file's W42-R1 placeholder filled with that pin" in first
    assert "**never re-run until it passes**" in s14
    assert "kept and labelled; the schedule-level overlap reported beside. **Kill:** an identity or a nested check " \
        "failing stops H4." in s11
    assert ("**Kill:** the oracle, the blank rule, the pairing, or an overlap count above 0 on any unit failing stops "
            "H4.") in s11
    assert "**The floors, each refusing" in s9, "the oracle and the overlap count are floors, not beside"
    floors = s9[s9.index("**The floors, each refusing"):]
    assert "**the zero-edge oracle, exactly, per trade:**" in floors
    assert "**the overlap count, per unit, on the taken trades** is 0 for every baseline and arm" in floors
    assert "equal to the code's count on every sampled unit" in floors
    bullets = [ln for ln in _section(text, 13).splitlines() if ln.startswith("- ")]
    assert bullets == [], "section 13 holds no bullet: no judged-block reads line"


def test_the_deciding_reading_and_the_pairing_are_held_exactly(text: str) -> None:
    """D13, D14, D6, D7, D4 and v2's section 5."""
    s7 = _section(text, 7)
    row = next(ln for ln in s7.splitlines() if ln.startswith("| the reading that decides |"))
    assert row.startswith("| the reading that decides | what W42-R1 reads | fixed | the martingale-outcome reading,")
    for phrase in ("L = min(l, c - x_stop) **fractional, never rounded** (E-237)", "p = L / (L + g)",
                   "L_fill = min(l, c - max(x_stop, x_flat)), fractional", "**the account is failed at the fill**",
                   "**the day stops**", 'there is no "not taken" state', "a driftless two-point race",
                   "`three_way_redraw.EXIT_LAW`, any other state refused"):
        assert phrase in row, phrase
    beside = next(ln for ln in s7.splitlines() if ln.startswith("| the readings beside |"))
    assert "never deciding" in beside and "**as-walked**" in beside
    assert ("| the responses | the firm's responses switched on | fixed | `off` only (0 % denial, the placement off, "
            "the Focused Trader Program off) |") in s7
    assert not re.search(r"`(denial|forfeit)_\d+`|`rtp(_w3)?`|`ftp_", text), "no response beyond off is named to run"
    flat = _flat(text)
    assert "0 to J - 1 (`three_way_runner.Plan`'s `seed_indices`), the same for every baseline and arm" in flat
    assert "**`J_H4` of Appendix A**: the smallest power of two at or above the J at which" in flat
    assert "on every search-year start of P-14 (and P-15, P-16 in H4-A)" in flat
    assert "not taken at the fill" not in flat


def test_the_nested_cuts(text: str, plan) -> None:
    """D10, m-4: three nested cuts against the search years' last day, the same in the text and the script."""
    s4 = _flat(_section(text, 4))
    assert ("the day blocks built on the cuts ending 2022-12-30, 2023-06-30 and 2023-09-29 must each equal those built "
            "on the cut ending 2023-12-29, block for block, up to their own last day") in s4
    assert "**the share of window sessions after 2023-09-29**" in s4
    assert plan.NESTED_CUTS == NESTED_CUTS
    assert "(2023-12-29, and 2022-12-30, 2023-06-30 and 2023-09-29 for the nested cuts)" in _flat(text)


# ------------------------------------------------------------------------------------------- the rulings, B-1 to B-7


def test_b1_the_strict_rule_and_the_overlap_count(text: str) -> None:
    flat = _flat(text)
    assert "**Stage 2's strict rule for every baseline** (D-409, D-429): one open position across all accounts" in flat
    assert "**no trade is copied across accounts**" in flat
    assert "**the per-unit overlap count on the taken-trade log must be 0** (section 7)" in flat
    assert "H3-A4" not in text.replace("the H3-A4 condition dropped", ""), "the copy check is dropped for H4"
    assert "seats" not in text and "copies of one trade" not in text and "copy one trade" not in text
    assert "never the one-uniform form" in flat


def test_b2_the_registered_constants_pass_through(text: str) -> None:
    flat = _flat(text)
    assert "**whole-window-derived registered comparators**" in flat
    assert "**the registered-constants file** (Appendix C), by its sha256 cited under a decision row" in flat
    assert "**search-year sub-hash** of the registered trades, computed once in the on-record whole-window identity run" \
        in flat and "(E-247 rm-4's exception), never by H4" in flat
    dep = _deps(text)
    assert "**the pass-through mode**" in dep["the cut, in its pass-through mode"]
    assert "never re-resolving them" in dep["the cut, in its pass-through mode"]
    assert "Q-172's count on P-14 is unaffected" in dep["the cut, in its pass-through mode"]
    assert "**to record** under its own row" in dep["the `trade_problems` switch-off"]
    assert "`SWITCHED_OFF`" in dep["the `trade_problems` switch-off"]
    assert "the check replaced, on cut rows only, by I-1's sub-hash comparison; whole-window builds keep it" \
        in dep["the `trade_problems` switch-off"]                                                     # E18


def test_b3_the_point_arm(text: str, plan) -> None:
    flat = _flat(text)
    assert '**`arm="point"`** for H4-A and for I-4\'s reference (E-248' in flat
    assert "**the verdict arm is never run**" in flat
    assert '"verdict"' not in text
    assert flat.count('run_starts(design, "point"') >= 3
    assert plan.AS_TRADED_ARM == "point"


def test_b4_one_collection_result(text: str, w42) -> None:
    s9 = _flat(_section(text, 9))
    assert "**To W42-R1: one collection result**" in s9 and "`results/h4_w42_input.csv`" in s9
    assert "**The adapter** is `extended/h4_collect.py::w42_readings(path, sidecar) -> {name: BaselineReading}`" in s9
    assert "each start's **uncapped** sessions left" in s9
    assert "**`orders_max`, `accounts_max` (measure (30)) and `taken_mean` (measure (37)), required now**" in s9
    assert "the run is refused without them" in s9
    s4 = _flat(_section(text, 4))
    assert "**The search calendar and sessions left, uncapped**" in s4 and "never capped" in s4
    assert "**the pinned search-year calendar H4 and W42-R1 both bind**, Q-197's result and its loader" in s4
    assert "**the start session counted as session 1**" in s4
    assert "ebd5a05" not in text, "the calendar is Q-197's, not the void calendar's day list"
    assert not getattr(w42, "OPTIONAL", None), "W42-R1 at 34ee968 has no optional measures"
    assert {"orders_max", "accounts_max", "taken_mean"} <= set(w42.REQUIRED)


def test_w42r1_second_texts_obligations(text: str, plan, w42) -> None:
    """W42-R1 (wt/wt-infra 34ee968, rm-1): its manifest fields with `arm` and the verdict settings, W an integer, the
    reading tag, first_pass_days, no optional measures, the collection's digest, the adapter's signature, the seed
    floor and the test's J, each held to its code."""
    s9 = _flat(_section(text, 9))
    assert "**Its sidecar carries every field of W42-R1's `H4_MANIFEST_KEYS`**" in s9
    for key in w42.H4_MANIFEST_KEYS:
        assert f"`{key}`" in s9, key
    assert "optional_measures" not in _section(text, 9), "W42-R1 at 34ee968 has no such field"
    assert "`readings_sha256` (`wave42.readings_digest` of the four readings, recorded by H4's collection, H4-C)" in s9
    assert "`calendar_sha256` (`wave42.calendar_digest`" in s9
    assert w42.ARM == "off" and "`arm` (`off`)" in s9
    assert w42.VERDICT == {"denial": 0.0, "placement": "off", "focused_trader": "off"}
    assert "`denial` (0), `placement` (`off`), `focused_trader` (`off`)" in s9
    assert w42.ADAPTER == "extended.h4_collect:w42_readings" and w42.COLLECTION_RESULT == "h4_w42_input.csv"
    assert "**H4 carries no held-out counts:** `wave42_apply` reads the pinned held-out calendar itself." in s9
    assert "taken on its bytes with CRLF normalised to LF" in s9
    assert "`sha256` at the sidecar's top level" in s9 and "under `write_result`'s `parameters`" in s9
    assert w42.READING == "martingale_outcome" and f"`reading` (`{w42.READING}`)" in s9
    assert w42.W == 126 and "`W` (126, an integer)" in s9
    assert "**126, pinned**" in _section(text, 7)
    assert "first_pass_days" in w42.REQUIRED and "`first_pass_days` (measure (1)" in s9
    assert (plan.H4_MIN_SEEDS, plan.TEST_SEEDS) == (w42.H4_MIN_SEEDS, w42.TEST_SEEDS)
    assert plan.j_provisional() >= w42.H4_MIN_SEEDS, "H4's J meets W42-R1's floor"
    assert f"H4_MIN_SEEDS = {w42.H4_MIN_SEEDS}: J (provisional) = {plan.j_provisional()} meets it" in plan.report()
    assert "**at least W42-R1's `H4_MIN_SEEDS`**" in _section(text, 7)
    assert "W42-R1's own declared `TEST_SEEDS`, not H4's" in _flat(_section(text, 10))
    dep = _deps(text)
    assert "**to build** (Q-197)" in dep["the search calendar"]
    assert "cited by the LF sha256 of all three files" in dep["W42-R1"] and "34ee968" in dep["W42-R1"]
    assert "`scripts/wave42_apply.py`" in dep["W42-R1"]
    assert "`search_calendar.csv`, W42-R1's `SEARCH_CALENDAR`" in dep["the search calendar"]
    assert w42.SEARCH_CALENDAR == "search_calendar.csv"


def test_b5_the_coins_identity(text: str) -> None:
    s16 = _flat(_section(text, 16))
    assert "**(I-5) the coin's source** (the lead's ruling on RB-1)" in s16
    assert ("at P-16's registered offered marks (the registered-constants file), latency 0, with P-16's `coin_table` "
            "sides and its `_nr` news rule, walked by `walker.STAGE2` (the breakeven move on), and produced by the "
            "vendored `resolved_coin.cell_trades`") in s16
    assert "**equals P-16's trigger-level trades by `rc_dev_test.trades_hash`** on the search years" in s16
    assert "with admission off, in the run's mode, its offers equal the clock grid less the void calendar" in s16
    assert "I-4 holds the firm path's routing to the vendored replay's" in s16


def test_b6_j_refused_until_w42r1_is_pinned(text: str, plan) -> None:
    if plan.W42_PIN is None:
        with pytest.raises(plan.W42NotPinned):
            plan.j_h4()
        assert W42_PLACEHOLDER in text, "the draft keeps its placeholder for W42-R1's pin"
        assert "J_H4: REFUSED until W42-R1 is pinned (B-6)" in plan.report()
    else:                                                     # once pinned: the row, the commit and the hash agree
        pin = plan.W42_PIN
        import hashlib

        dec = _lf(ROOT / "DECISIONS.md")
        row = next(ln for ln in dec.splitlines() if ln.startswith(f"| {pin['row']} |"))
        assert W42_PLACEHOLDER not in text
        for key, path in (("rule_sha256", "docs/plans/WAVE42_SETTING_RULE.md"), ("code_sha256", "extended/wave42.py"),
                          ("script_sha256", "scripts/wave42_apply.py")):
            assert pin[key] in text and pin[key] in row, key                  # all three files, cited (rm-1)
            lf = _show(pin["commit"], path).replace("\r\n", "\n")
            assert hashlib.sha256(lf.encode("utf-8")).hexdigest() == pin[key], path
        assert plan.j_h4() == plan.j_provisional()
    assert "H4 pins after W42-R1" in plan.__doc__


def test_b7_the_held_out_read_ledger(text: str) -> None:
    s2 = _section(text, 2)
    table = [ln for ln in s2.splitlines() if ln.startswith("  | ") and "---" not in ln][1:]
    assert len(table) >= 12, "every inherited whole-window choice is an entry"
    joined = "\n".join(table)
    for need in ("D-554", "D-525", "E-203 S-2", "D-502", "D-509", "capacity", "rung map", "Q-132", "Q-16",
                 "Q-17", "E-201", "RD-02", "RD-03", "RD-04", "RD-05", "program U", "the lead's fixed choice"):
        assert need in joined, need
    flat = _flat(s2)
    assert '"written after this reading; no figure cited"' in flat
    assert "**the level is nominal** (CHARTER 3.6 (b))" in flat
    assert "fixed, **the lead's fixed choice**" in _section(text, 7)
    for need in ("D-626", "Stage 2's signal search", "RD-01", "D-518", "D-620 (3)(f)", "Q-44", "`EXACT`",
                 "**P-16's window `all`**", "D-525 (3)", "**the registered-constants run itself**"):   # rm-3
        assert need in joined, need


def test_the_minors(text: str) -> None:
    flat = _flat(text)
    assert "can therefore move delta\\* **either way**" in flat                                     # m-2
    assert "**a real read**" in flat and "**its outputs written sealed**" in flat                     # m-3
    assert "The coin differs from P-16 in its schedule" in flat and "its latency (L = 5" in flat       # m-5
    assert "in its schedule alone" not in flat
    m35 = _flat(_between(_lf(MEASURES), "### (35) Naive coin harvesting", "### (36)"))
    assert "**its levers fixed in H4's declaration**" in m35 and "Wave 5's search declaration adopts" in m35  # m-6


def test_every_finding_is_answered_once(text: str) -> None:
    table = _between(text, "<!-- h4_findings: begin -->", "<!-- h4_findings: end -->")
    ids = re.findall(r"^\| (B-\d|m-\d) \|", table, re.MULTILINE)
    assert tuple(ids) == FINDINGS
    assert "| template v2 |" in table
    table2 = _between(text, "<!-- h4_findings_c2: begin -->", "<!-- h4_findings_c2: end -->")
    assert tuple(re.findall(r"^\| (RB-\d|rm-\d|rn-\d) \|", table2, re.MULTILINE)) == FINDINGS_C2


# -------------------------------------------------------------------------------------------- the dependencies


def _deps(text: str) -> dict[str, str]:
    dep = _between(text, "<!-- h4_dependencies: begin -->", "<!-- h4_dependencies: end -->")
    rows = [r for r in dep.splitlines() if r.startswith("| ") and not r.startswith("| dependency") and "---" not in r]
    return {r.split("|")[1].strip(): r for r in rows}


def test_the_dependencies_are_named(text: str) -> None:
    by = _deps(text)
    want = ("the seed-paired runner", "the firm path", "the cut, in its pass-through mode", "the registered-constants file",
            "the `trade_problems` switch-off", "the collection and its adapter", "the seed module's H4 block", "W42-R1",
            "the search calendar", "the starts and the as-traded replays", "the measures", "the naive coin's source",
            "the walk", "the reader")
    assert tuple(by) == want, tuple(by)
    for r in by.values():
        cells = [c.strip() for c in r.split("|")[1:-1]]
        assert len(cells) == 4 and all(cells), r
        assert len(cells[3]) > 60, f"what H4 needs from {cells[0]} is stated: {cells[3]!r}"
    assert "`extended/three_way_runner.py` on wt/wt-three adedf7f" in by["the seed-paired runner"]
    assert "RB-1" in by["the seed-paired runner"]
    assert "**Q-185**" in by["the firm path"] and "**built; to correct for H4** (rc-4)" in by["the firm path"]
    assert "**any overlap refused**" in by["the firm path"] and "**required**" in by["the firm path"]
    assert "`vendor/stage2/propedge/campaign/lockstep.py`" in by["the firm path"]
    assert "`extended/search_cut.py` (E-248, built on wt/wt-user)" in by["the cut, in its pass-through mode"]
    assert "**as pinned**" in by["W42-R1"] and "2bde318" in by["W42-R1"]
    for commit, path in ((RUNNER_COMMIT, "extended/three_way_runner.py"), (RUNNER_COMMIT, "extended/three_way_seeds.py"),
                         (PROVISIONAL_W42, "docs/plans/WAVE42_SETTING_RULE.md"), (PROVISIONAL_W42, "extended/wave42.py")):
        assert _git("cat-file", "-e", f"{commit}:{path}", check=False).returncode == 0, (commit, path)
    runner = _show(RUNNER_COMMIT, "extended/three_way_runner.py")
    for name in ("class Plan", "def stress_arms", "def paired", "def matrix", "class HeldOutRefused",
                 'BASELINES = ("naive_coin", "p14", "p15", "p16")'):
        assert name in runner, name
    assert (ROOT / "vendor" / "stage2" / "propedge" / "campaign" / "lockstep.py").is_file()
    vend = (ROOT / "vendor" / "stage2" / "scripts" / "rc_dev_test.py").read_text("utf-8")
    assert "def trade_problems(" in vend and "def trades_hash(" in vend


def test_the_built_dependencies_hold_the_names_h4_uses() -> None:
    import inspect

    from extended import components, journey_measures, journey_readings, triggers, user_beside

    assert "search" in user_beside.JOURNEY_BLOCK_NAMES and "off" in user_beside.BY_NAME
    assert user_beside.BY_NAME["off"].kind == "off" and user_beside.BY_NAME["off"].enforcement_p == 0.0
    sig = inspect.signature(user_beside.run_starts).parameters
    assert list(sig)[:2] == ["design", "arm"] and "journey" in sig and "journey_block" in sig
    vend = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "user_journey.py").read_text("utf-8")
    assert 'ARMS = ("verdict", "point")' in vend, "the point arm is one of U1's two"
    for f in ("coin_readings", "design_coin_readings", "variance_decomposition", "peak_oop", "bankroll_stop",
              "workload", "supply"):
        assert callable(getattr(journey_measures, f)), f
    assert callable(journey_readings.summary)
    assert hasattr(triggers, "CoinMarks") and callable(components.coin_component)
    assert callable(components.schedule_day)
    assert (ROOT / "extended" / "router.py").is_file()


# --------------------------------------------------------------------------------- the measures and W42-R1's keys


def test_every_measure_is_placed(text: str) -> None:
    index = _between(_lf(MEASURES), "<!-- measures-index:start -->", "<!-- measures-index:end -->")
    theirs = [int(m) for m in re.findall(r"^\| (\d+) \|", index, re.MULTILINE)]
    table = _between(text, "<!-- h4_measures: begin -->", "<!-- h4_measures: end -->")
    rows = re.findall(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", table, re.MULTILINE)
    assert [int(r[0]) for r in rows] == theirs, "every measure of the index, once each, in order"
    allowed_where = {"W", "21", "63", "126", "252", "63, 126, 252", "each month", "—", "each headline's",
                     "each measure's", "the search years", "W, its share paid beside"}
    for n, _, status, where, _ in rows:
        s = status.strip()
        assert s.startswith(("read", "**not read**", "its ingredients read", "the comparator")), (n, s)
        assert where.strip() in allowed_where, (n, where)
        assert "where the firm path emits" not in s, "no measure is left to a build (B-4)"
    by = {int(r[0]): r for r in rows}
    assert by[33][2].strip().startswith("**not read**")
    assert "10 %" in by[28][2] and "+1 tick" in by[29][2]


def test_every_w42_input_is_named(text: str, w42) -> None:
    keys = set(w42.REQUIRED) | set(getattr(w42, "OPTIONAL", {}) or {})
    sec = _flat(_section(text, 9))
    table = _between(text, "<!-- h4_measures: begin -->", "<!-- h4_measures: end -->")
    for k in sorted(keys):
        if re.fullmatch(r"(net|peak)_month_\d", k):
            stem = k.rsplit("_", 1)[0]
            assert f"`{stem}_1` to `{stem}_3`" in sec, k
            assert f"`{k}`" in table, k
        else:
            assert f"`{k}`" in sec and f"`{k}`" in table, k
    for k in ("P_B", "`run_out`", "`not_paid_within_B`", "the per-unit spending before the first payout"):
        assert k in sec, k
    assert w42.BASELINES == ("naive_coin", "p14", "p15", "p16") and w42.BLOCK == "search"


# --------------------------------------------------------------------------------------------- the plan, and J


def _appendix(text: str) -> str:
    block = _between(text, "<!-- h4_plan: begin -->", "<!-- h4_plan: end -->").strip()
    assert block.startswith("```text\n") and block.endswith("\n```")
    return block[len("```text\n"):-len("\n```")]


def test_the_plan_is_the_scripts(text: str, plan) -> None:
    assert _appendix(text) == plan.report()


def test_the_scripts_constants_are_their_sources(plan, w42) -> None:
    from extended import family_stats, user_beside

    assert plan.PROVISIONAL_W42_COMMIT == PROVISIONAL_W42
    assert (plan.RESOLVE_Z, plan.DELTA_MIN, plan.W42_W) == (w42.RESOLVE_Z, w42.DELTA_MIN, w42.W)
    assert plan.POWER == w42.POWER_TARGET == family_stats.MDL_POWER
    assert plan.BASELINES == w42.BASELINES
    assert plan.EXACT_EVERY == user_beside.EXACT_EVERY
    assert plan.WINDOWS == (w42.W, 252) and plan.DIM_HORIZONS == tuple(sorted({d.horizon for d in w42.DIMENSIONS}))
    vend = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "user_journey.py").read_text("utf-8")
    assert f"EXACT = {plan.EXACT!r}" in vend
    assert plan.A.SEARCH == ("2020-01-02", "2023-12-29") and plan.SEARCH_YEARS == 4
    assert plan.HOLIDAYS_A_YEAR == 12 and plan.BATCH_STARTS == 21                 # P1, P6
    assert "a batch of 21 starts" in _lf(DRAFT)


def _weekdays() -> int:
    import numpy as np

    return int(np.busday_count(np.datetime64("2020-01-02"), np.datetime64("2023-12-30")))


def _z(p: float) -> float:
    from scipy import stats

    return float(stats.norm.ppf(p))


def test_j_recomputed_from_the_formula(plan) -> None:
    """P1, P3, P5: J_needed exactly, from the formula here, not from the script's own functions."""
    z = _z(plan.POWER)
    n_units = math.ceil(((plan.RESOLVE_Z + z) / plan.DELTA_MIN) ** 2)
    lower = _weekdays() - 12 * 4
    need = math.ceil(n_units / (lower - 252 + 1))
    assert plan.units_needed() == n_units and plan.j_needed() == need
    J = plan.j_provisional()
    assert J >= need and J & (J - 1) == 0 and J < 2 * need, (J, need)
    for h in (63, 126, 252):
        assert (plan.RESOLVE_Z + z) / math.sqrt(J * (lower - h + 1)) <= plan.DELTA_MIN


def test_the_appendixs_figures_recomputed(text: str, plan) -> None:
    """P2, P4: the printed gaps and the parts' work, from the formulas here."""
    app = _appendix(text)
    z, J = _z(plan.POWER), plan.j_provisional()
    up, lo = _weekdays(), _weekdays() - 48
    for h in (63, 126, 252):
        hi_gap = (plan.RESOLVE_Z + z) / math.sqrt(J * (lo - h + 1))
        lo_gap = (plan.RESOLVE_Z + z) / math.sqrt(J * (up - h + 1))
        assert f"h={h}: gap resolved with probability POWER from {lo_gap:.4f} to {hi_gap:.4f}" in app, h
    exact = (21, 63, 90, 126)
    every = 1 + sum(exact) / 252
    stress = 1 + sum(exact) / 252 / 21
    work = J * up * 252 * 4 * (2 * every + 2 * stress)
    for b in ("naive_coin", "p14", "p15", "p16"):
        line = next(ln for ln in app.splitlines() if ln.startswith(f"  H4-B {b}"))
        assert f"| {work:.3e} lane-trades |" in line, line
        hours = [float(x) for x in line.split("lane-trades |")[1].split("|")[0].split()]
        assert hours == [round(work * c * 1e-6 / 2 / 3600, 1) for c in (0.05, 0.5, 5.0)]
        assert work * 5.0e-6 / 2 / 3600 <= 8, "each part fits its cap at the largest assumed cost"
    assert J * 21 <= plan.A.max_lanes()
    assert len(plan.ARM_RUNS) == 4 and {a for a, _, _ in plan.ARM_RUNS} == {"off", "worse_1", "missed_0.1"}


def test_the_responses_and_the_stress_arms(text: str) -> None:
    flat = _flat(text)
    for phrase in ("`off` only", "`worse_1`", "`missed_0.1`", "the runner's `worse_2` arm is not run by H4",
                   "0 % payout denial, the placement off, the Focused Trader Program off"):
        assert phrase in flat, phrase


# ------------------------------------------------------------------------------------------- cycle 2: RB-1 to rn-4


def test_rb1_the_coins_unchained_offers(text: str) -> None:
    s5 = _flat(_section(text, 5))
    for phrase in ("**the naive coin's offers** (the lead's ruling on RB-1)", "**unchained**",
                   "never `components.schedule_day`'s chain at one R, never Q-169's router",
                   "**walked at every R of P-16's table**", "`resolved_coin.cell_trades`",
                   "drawn **once per (session, moment) from the coin's schedule-side seed** (section 15), independent of "
                   "the seed index", "**one schedule, built once**",
                   "the vendored routing the registered designs use"):
        assert phrase in s5, phrase
    s3 = _flat(_section(text, 3))
    assert "**the naive coin's unchained offers through the same vendored routing** (`shared_days.TradeRouter`" in s3
    assert "mix router" not in text and "Q-169's router" in text
    dep = _deps(text)
    assert "**re-built as an unchained offer list**" in dep["the naive coin's source"]
    assert "`shared_days.TradeRouter`" in dep["the firm path"] and "`can_take`" in dep["the firm path"]
    vend = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "resolved_coin.py").read_text("utf-8")
    for name in ("def marks(", "def coin_table(", "def cell_trades(", "MARK_STEP = 5", 'WINDOWS = {"all"'):
        assert name in vend, name
    sd = (ROOT / "vendor" / "stage2" / "propedge" / "campaign" / "shared_days.py").read_text("utf-8")
    assert "class TradeRouter" in sd and "can_take" in sd


def test_rb2_the_per_unit_overlap_count(text: str) -> None:
    s7 = _flat(_section(text, 7))
    assert ("**The refusing count is per unit** (start, seed) and per arm, **on the taken trades**: any two taken "
            "trades of the user whose spans **[fill bar end, exit bar end at the taken R + 5 min)** intersect, **on "
            "Stage 2's bar-end clock**") in s7
    assert "it must be 0, **written for every unit**, and **the auditor recomputes it from the sampled units' logs, " \
        "without the enforcing code**, equal to the code's count on every sampled unit" in s7
    s5 = _flat(_section(text, 5))
    assert "**The schedule-level overlap, beside, never a kill**" in s5
    assert "**the positions open at once**" not in text
    s16 = _flat(_section(text, 16))
    assert "**the per-unit overlap count recomputed from the sampled units' logs alone, without the enforcing code**" \
        in s16
    assert "`results/h4_trades_<baseline>.csv`: the full taken-trade log **of the audit sample's units only** (rc-3)" \
        in s16
    assert "the schedule-level overlap beside, per baseline and search year" in s16
    s17 = _flat(_section(text, 17))
    assert ("a second trade whose fill bar ends exactly five minutes after the first's exit bar ends (admitted, count "
            "0) and one whose fill bar ends four minutes after (count 1, refused), and the vendored router's admitted "
            "boundary pair counting 0 (RC-2)") in s17


def test_rm2_the_surviving_mutants_sentences(text: str, plan) -> None:
    """E1 to E28 of the re-read, each held by its sentence."""
    flat = _flat(text)
    s = {n: _flat(_section(text, n)) for n in range(20)}
    checks = {
        "E4": (s[2], "passed in **as registered**, never re-resolved on the search years"),
        "E5": (s[16], "each close's `rel` within a millionth of a dollar (MEASURES 1.2's tolerance)"),
        "E6": (s[11], "H4-A's replays of the same starts must reproduce that hash"),
        "E7": (s[14], "nothing of H4 is read by W42-R1 until every part is complete"),
        "E8": (s[3], "one open position across all accounts, five minutes flat, each trade to one account"),
        "E9": (s[2], "H4 does not read them"),
        "E10": (s[9], "**on the deciding `off` reading** (never the as-walked or as-traded reading)"),
        "E11": (s[16], "the registered-constants file on record by its sha256"),
        "E13": (s[16], "computed once in the on-record whole-window identity run (E-247 rm-4's exception), never by H4"),
        "E14": (s[9], "it refuses a file whose sha256 differs from its sidecar's, any declared start, seed or key "
                      "missing, readings not paired, or a `readings_sha256` its readings do not reproduce"),
        "E15": (s[12], "the share of window sessions after the last nested cut on every twelve-month and W = 252 reading"),
        "E16": (s[7], "each on every baseline alike, on the deciding reading, on the same keys as `off`"),
        "E17": (s[7], "P-16's registered window `all` (`resolved_coin.WINDOWS`, 17:00 CT to the cutoff)"),
        "E20": (s[16], "recomputed from the schedules and keys through the firm path, equal bit for bit"),
        "E21": (s[9], "for every taken trade, the race's p g - (1 - p) L is zero"),
        "E21b": (s[16], "the oracle re-checked on the trade logs from the logged inputs alone, for every taken trade"),
        "E22": (s[9], "the key guard's sample holding (`three_way_keys.KeyGuard.sampled`)"),
        "E24": (s[18], "**W42-R1 pinned first**"),
        "E25": (s[4], "every session of the search years is a start, the same set for every baseline, arm and seed"),
        "E26": (s[11], "each baseline's schedule and the identities I-1 and I-5"),
        "E27": (s[7], "its stop (`rc150_dev_test.STOP`)"),
        "E28": (s[8], "the held-out test's level stays nominal while the held-out read ledger is not empty"),
    }
    for name, (sec, phrase) in checks.items():
        assert phrase in sec, (name, phrase)
    assert "recomputed by H4" not in flat                                                              # E13
    assert "for a sample of taken trades" not in flat                                                  # E21
    body19 = [ln for ln in _section(text, 19).strip().splitlines()[1:] if ln.strip() and ln.strip() != "---"]
    assert body19 == ["*(Empty at the pin.)*"]                                                        # E12
    assert ("the crash rule: no reading is made until every part completes; a crashed part is re-run whole from its "
            "declared seeds, never resumed; each crash is recorded in the part ledger (E-195)") in plan.report()  # E23
    vend = (ROOT / "vendor" / "stage2" / "scripts" / "rc150_dev_test.py").read_text("utf-8")
    assert re.search(r"^STOP = \d+", vend, re.MULTILINE), "the coin's stop is the vendored P-16 cell's"     # E27
    s9 = s[9]
    collection = s9[s9.index("**To W42-R1: one collection result**"):s9.index("**The keys**")]
    assert "as-walked reading" not in collection.replace("never the as-walked or as-traded reading", ""), "E10"


def test_rm4_to_rm6_and_the_notes(text: str) -> None:
    flat = _flat(text)
    dep = _deps(text)
    reg = dep["the registered-constants file"]
    assert "**copied, by sha256, from the registered result files**" in reg and "**computed: only** the search-year " \
        "sub-hash" in reg                                                                                   # rm-4
    s16 = _flat(_section(text, 16))
    assert ("whose **trading day** (A1's `date` column, never the clock date: the evening session opening the trading "
            "day 2024-01-02 belongs to it and is excluded)") in s16                                       # rm-4, rc-8
    assert "evening of 2023-12-29" not in text
    s11 = _flat(_section(text, 11))
    assert "its job **built through the cut in its pass-through mode** (rm-5)" in s11
    assert "the runner **refuses a job whose calendar does not end on 2023-12-29**" in s11                  # rm-5
    assert "every job's calendar ending on 2023-12-29" in s16
    s4 = _flat(_section(text, 4))
    assert "**It must equal the cut's A1 day list date for date, or it is refused** (rm-6)" in s4
    assert "**its two start sets compared** first" in s16                                                   # rm-6
    assert "**equal to the cut's A1 day list date for date, refused otherwise** (rm-6)" in dep["the search calendar"]
    gi = _lf(ROOT / ".gitignore")
    assert re.search(r"^\.h4_dev/$", gi, re.MULTILINE), "the worker's scratch is git-ignored (rn-1)"
    assert ".h4_dev" not in SKIP_DIRS
    assert "**re-checked against the template's third text when v3 is pinned** (rn-2)" in flat
    assert "H4 is not a search and enters no membership" in flat                                             # rc-7
    assert "they serve a member search only if that search's hash row cites H4's pin row" in flat
    assert "H4's values are void for that search" not in flat
    assert "a same-day look-ahead on supply, small, printed beside the coin's supply count" in flat          # rn-3
    assert "**at the run's own exit times** -- the real path's exits at each trade's taken R" in flat        # rn-4


# ------------------------------------------------------------------------------------------- text 4: RC-1 to rn-e


def _span_count(trades, gap: float = 5.0) -> int:
    """The declared count (section 7): pairs whose [fill bar end, exit bar end + gap) spans intersect, on Stage 2's
    bar-end clock -- computed here from the declared rule, never by the firm path's code."""
    spans = [(float(e), float(x) + gap) for e, x in trades]
    return sum(1 for a in range(len(spans)) for b in range(a + 1, len(spans))
               if spans[a][0] < spans[b][1] and spans[b][0] < spans[a][1])


def test_rc2_the_span_on_stage2s_clock() -> None:
    """D-429's boundary: a fill bar ending exactly five minutes after the exit bar ends is admitted and counts 0; four
    minutes after counts 1."""
    assert _span_count([(1, 6), (11, 20), (26, 40)]) == 0
    assert _span_count([(1, 6), (10, 20)]) == 1
    assert _span_count([(1, 6), (11, 20)]) == 0


ROUTER_PROBE = """
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from propedge.campaign.shared_days import TradeRouter

class Table:
    def historical_day(self, d):
        return 0

def routed(entry, exit_):
    r = TradeRouter(Table(), [len(entry)], [(np.array(entry, float), np.array(exit_, float))], one_at_a_time=5.0)
    keys = [("combine", 0), ("combine", 1)]
    r.begin_day(0, keys)
    return sorted(j for k in keys for j in r._assigned[k])

print(routed([1, 11, 26], [6, 20, 40]))
print(routed([1, 10], [6, 20]))
"""


def test_rc2_the_vendored_routers_boundary_pair_counts_0(tmp_path: Path) -> None:
    """The vendored `TradeRouter` (run in its own process, nothing vendored edited) admits the boundary pair, which the
    declared count counts 0; the pair one minute inside is refused by the router and counted 1 by the rule."""
    script = tmp_path / "router_probe.py"
    script.write_text(ROUTER_PROBE, encoding="utf-8")
    out = subprocess.run([sys.executable, str(script), str(ROOT / "vendor" / "stage2")], capture_output=True,
                         text=True, timeout=300, env={**__import__("os").environ, "OMP_NUM_THREADS": "1"})
    assert out.returncode == 0, out.stderr
    first, second = (ast.literal_eval(ln) for ln in out.stdout.strip().splitlines())
    assert first == [0, 1, 2] and _span_count([(1, 6), (11, 20), (26, 40)]) == 0, "the boundary pair is admitted"
    assert second == [0] and _span_count([(1, 6), (10, 20)]) == 1, "one minute inside is refused"


def test_rc1_the_breakeven_law_and_the_coins_walk(text: str) -> None:
    s7 = _flat(_section(text, 7))
    assert "| **the breakeven move's law** |" in s7
    for phrase in ("**every trade whose move bar comes before its time limit, whatever its historical kind**",
                   "**the move-aware sequential race, time-limited, the exact law**",
                   "**(1) to the move bar**: R-10's stopped walk from the fill to the move bar's open between -L and +g, "
                   "**its step count taken from the time to the move bar**",
                   "**(2) the move arms** at that open if the walked position x is at least one tick in the trade's favour",
                   "**the stop becomes the entry** (zero gross)",
                   "**(3) from x to the trade's time limit, bounded by it**: R-10's stopped walk from x between the entry "
                   "(armed) or -L (not armed) and +g",
                   "Its gross expectation is exactly zero (optional stopping at each stage)",
                   "L_fill = min(l, c - max(x_stop, x_flat, x_b))"):
        assert phrase in s7, phrase
    assert ("**`walker.STAGE2`, P-16's walk, FV3's breakeven move on** (the lead's ruling on RC-1)") in s7
    assert "`triggers.JOURNEY`'s move-off walk is never used for it" in s7
    assert "**The lever table's S7 (the move dropped) governs designs, and does not apply to H4's coin**" in s7
    assert "it walks as P-16 does (`walker.STAGE2`, the breakeven move on)" in s7
    s5 = _flat(_section(text, 5))
    assert "**by P-16's walk**, `walker.STAGE2`, FV3's breakeven move on" in s5 and "**the breakeven exits**" in s5
    dep = _deps(text)
    assert "**the `b` state to build** (RC-1)" in dep["the seed-paired runner"]
    assert "**the breakeven state carried** -- `EXIT_LAW` gains `b`" in dep["the seed-paired runner"]
    assert "never `triggers.JOURNEY`" in dep["the naive coin's source"]
    assert "`STAGE2`" in dep["the walk"]
    fv3 = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "fv3_rung_walk.py").read_text("utf-8")
    assert "BREAKEVEN" in fv3 and "be_open" in fv3 and "SESSION_OPENS" in fv3
    walker = (ROOT / "extended" / "walker.py").read_text("utf-8")
    assert re.search(r"^STAGE2\s*=", walker, re.MULTILINE), "the walker's STAGE2 preset exists"
    trig = (ROOT / "extended" / "triggers.py").read_text("utf-8")
    assert re.search(r"^JOURNEY\s*=", trig, re.MULTILINE)


def test_rc3_the_audit_sample(text: str, plan) -> None:
    s7 = _flat(_section(text, 7))
    assert ("| the audit sample | the units whose full taken-trade log is written (rc-3) | fixed | 1 % of units (start, "
            f"seed index), every arm, drawn by {H4_BLOCK[4]} (section 15)") in s7
    s16 = _flat(_section(text, 16))
    assert "free disk at least twice the audit sample's log size Appendix A prints (rc-3)" in s16
    assert "the per-unit overlap counts, every unit and arm, a column of `results/h4_units_<baseline>.csv`" in s16
    assert (plan.SAMPLE_SHARE, plan.DISK_FACTOR) == (0.01, 2)
    rows = round(plan.SAMPLE_SHARE * plan.j_provisional() * _weekdays() * 4 * 252 * 4)
    total = rows * plan.LOG_ROW_BYTES * 4
    assert (f"at most {rows} rows a baseline at {plan.LOG_ROW_BYTES} B a row: {total / 1e9:.2f} GB over the four "
            f"baselines; the run is refused unless 2 x that, {2 * total / 1e9:.2f} GB, is free on disk") in plan.report()


def test_rc4_the_firm_paths_baseline_mode(text: str) -> None:
    fp = _deps(text)["the firm path"]
    for phrase in ("`extended/three_way_firm.py` on wt/wt-firmpath de1049e or later",
                   "routing through the vendored `TradeRouter` (the strict rule at each account's R, `can_take`), never "
                   "Q-169's router plus refusal", "same-bar exits allowed, `entry <= exit` on Stage 2's clock",
                   "the `b` state", "every R of P-16's table carried"):
        assert phrase in fp, phrase
    assert "**the firm path (Q-185) corrected for H4's baseline mode at a named commit**" in _flat(_section(text, 18))
    assert _git("cat-file", "-e", "de1049e^{commit}", check=False).returncode == 0


def test_rc5_the_survivors_sentences(text: str) -> None:
    s7, s3, s16 = (_flat(_section(text, n)) for n in (7, 3, 16))
    dep = _deps(text)
    checks = {
        "N1": (s7, "applied by the vendored routing, `shared_days.TradeRouter`"),
        "N3": (_flat(_section(text, 15)), "history 0, seed index 0 and start 0 (the schedule is no user's), so "
                                          "independent of every seed index"),
        "N5": (_flat(_section(text, 5)), "exit bar end at the largest R + 5 min)"),
        "N6": (s7, "each offer carries every R of P-16's table"),
        "N14": (s3, "the naive coin under E-223's one convention through the trigger library"),
        "N17": (s16, "Q-197's calendar equal to the cut's A1 day list (section 4)"),
        "N19": (s7, "the firm path refuses any overlap"),
        "N21": (dep["the naive coin's source"], "not `schedule_day`'s chain, not `extended/router.py`"),
        "N24": (s7, "the as-run side drawn once per (session, moment) from the coin's schedule-side seed (section 15)"),
        "N25": (dep["the naive coin's source"], "an admission restricted to a given mark list at latency 0 with given "
                                               "sides and news rule, for I-5"),
        "N27": (s16, "(E-248's point-arm start-row identity of P-14 held beside, as the cut's own)"),
    }
    for name, (sec, phrase) in checks.items():
        assert phrase in sec, (name, phrase)
    assert "`extended/router.py`" not in s7 and "Q-169's router" not in s7.replace("never Q-169's router", "")


def test_rc6_i5s_day_set_and_columns(text: str) -> None:
    s16 = _flat(_section(text, 16))
    assert "built on A1's walked days (kinds `n` and `b`) with Q-166's void calendar off, D-533's cut" in s16
    cols = ("`date`, `year`, `decision_ct`, `day_kind`, `decision_slot_minutes`, `S`, `stop_ticks`, `entry_t`, `side`, "
            "`fee_micro_eq`, then at each of `fv3_rung_walk.RR_GRID`'s twelve Rs `r_R`, `g_R`, `c_R`, `mae_R`, "
            "`exit_t_R` and `o_R`, then `exit_t` and `flat` at `fresh_rr`")
    assert cols in s16
    rc = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "resolved_coin.py").read_text("utf-8")
    body = rc[rc.index("def cell_trades("):rc.index("# ====", rc.index("def cell_trades("))]
    for c in ("date", "year", "decision_ct", "day_kind", "decision_slot_minutes", "stop_ticks", "entry_t", "side",
              "fee_micro_eq", "exit_t", "flat"):
        assert f'"{c}"' in body, c
    for c in ("r_", "g_", "c_", "mae_", "exit_t_", "o_"):
        assert f'f"{c}{{R:g}}"' in body, c
    fv3 = (ROOT / "vendor" / "stage2" / "propedge" / "research" / "fv3_rung_walk.py").read_text("utf-8")
    assert "RR_GRID = tuple(0.25 * k for k in range(1, 13))" in fv3, "twelve Rs"


def test_rc9_to_rc13(text: str, plan) -> None:
    import hashlib

    dep = _deps(text)
    assert "**its pre-pin fix at c72526d**, merged as 75ff709" in dep["W42-R1"]
    assert ("**its final commit c014d0a**, where the public `composite_per_seed`, `limit_estimate` and `null_journeys` "
            "have landed and `DO_NOTHING_EPS` is to be declared") in dep["W42-R1"]
    assert plan.PROVISIONAL_W42_COMMIT == "c014d0a"
    w = _show("c014d0a", "extended/wave42.py")
    for fn in ("def composite_per_seed(", "def limit_estimate(", "def null_journeys("):
        assert fn in w, fn
    reg = dep["the registered-constants file"]
    cap = ROOT / "vendor" / "stage2" / "results" / "a3_brk30_cb20_gate.csv.manifest.json"
    sha = hashlib.sha256(cap.read_bytes()).hexdigest()
    assert f"`vendor/stage2/results/a3_brk30_cb20_gate.csv.manifest.json`, sha256 `{sha}`" in reg, "rc-10"
    assert '"trades_per_day_capacity"' in cap.read_text("utf-8") and "`trades_per_day_capacity`" in reg
    s7 = _flat(_section(text, 7))
    assert "**no booked value lies outside the trade's [-(stop + costs), +(target - costs)]** (rc-11)" in s7
    assert "a flipped target never booked as -g" in s7
    assert 'labelled "the as-walked reading at the run\'s exits, bounded"' in s7
    assert "both exits logged (rc-12)" in s7
    assert "the exit at the taken R and the router's latest exit (rc-12)" in _flat(_section(text, 16))
    assert "| template v3's section 5 |" in s7                                                               # rc-13
    for item in ("**L_race** = min(l, c - x_stop), not L_fill", "**zero contracts at a positive room: the account "
                 "ends out of room**", "**the lattice step s per trade** (S-1)", "**T known at the fill for every row**",
                 "**the both-barriers-in-one-step rule**", "**the time exit's clip credit printed beside**",
                 "**a daily loss limit at or below e + max(x_stop, x_flat) refused**"):
        assert item in s7, item
    assert "**the accounts ended out of room** (v3's section 5)" in _flat(_section(text, 12))
    assert "out of room" in _show("13df998", "prereg/TEMPLATE_design_search.md")


def test_the_notes_rn_a_to_rn_e(text: str) -> None:
    flat = _flat(text)
    assert "D-429's five minutes are four to five minutes of real flat time" in flat                   # rn-a
    assert "**The coin's schedule side** (rn-c) is another draw" in _flat(_section(text, 6))            # rn-c
    assert "dropped before they are parsed (rn-d); no figure" in flat                                  # rn-d
    assert "**the held-out manifest entries dropped before they are parsed** (rn-d)" in flat
    s3 = _flat(_section(text, 3))
    assert "**The breakeven move**" in s3 and "10305426" in s3 and "E-012" in s3 and "S7" in s3       # rn-e


def test_appendix_f_answers_every_finding(text: str) -> None:
    table = _between(text, "<!-- h4_findings_c3: begin -->", "<!-- h4_findings_c3: end -->")
    ids = tuple(re.findall(r"^\| (RC-\d|rc-\d+|rn-a to rn-e) \|", table, re.MULTILINE))
    assert ids == FINDINGS_C3


SEED_MODULE_COMMIT = "cb1ff6c"


def test_the_seed_block_is_the_seed_modules() -> None:
    """The draft's parts and role names are the seed module's at wt/wt-three cb1ff6c, the block's values its
    `H4_ROLES`; the audit sample's role is the spare `h4_spare_4`, still unregistered there."""
    src = _show(SEED_MODULE_COMMIT, "extended/three_way_seeds.py")
    tree = ast.parse(src)
    env = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            if isinstance(target, ast.Name) and target.id in ("H4_ROLES", "PARTS"):
                env[target.id] = node.value
    roles = ast.literal_eval(env["H4_ROLES"])
    assert sorted(roles.values()) == list(H4_BLOCK), "the module's H4 block is this draft's"
    parts_src = ast.get_source_segment(src, env["PARTS"])
    for name, pid in (("H4-0", 10), ("H4-B", 11), ("H4-T", 12), ("H4-S", 13)):
        assert f'"{name}": {pid}' in parts_src, name
    assert roles["h4_tests"] == H4_BLOCK[0] and roles["h4_0_probe"] == H4_BLOCK[1]
    assert roles["h4b_coins"] == H4_BLOCK[2] and roles["h4s_schedule_side"] == H4_BLOCK[3]
    assert roles["h4_spare_4"] == H4_BLOCK[4] and "h4b_audit_sample" not in roles, "to register by wt-three"
    text = _lf(DRAFT)
    table = _section(text, 15)
    for role, i in (("h4_tests", 0), ("h4_0_probe", 1), ("h4b_coins", 2), ("h4s_schedule_side", 3),
                    ("h4b_audit_sample", 4)):
        assert re.search(rf"^\| {H4_BLOCK[i]} \| `{role}`", table, re.MULTILINE), role


def test_the_firm_paths_baseline_laws(text: str) -> None:
    """The laws the lead ruled for the firm path's baseline mode (BUILD_FIRMPATH_c2_2026-11-21), declared alike here."""
    s7 = _flat(_section(text, 7))
    for phrase in (
            "**every trade whose move bar comes before its time limit, whatever its historical kind**",      # 1
            "**(3) from x to the trade's time limit, bounded by it**",                                     # 1
            "**Beside:** both breakeven shares, the redrawn one and FV3's historical one",                  # 1
            "**its step count taken from the time to the move bar**",                                      # 2
            "a need-aware exit drawn by the `profit_level` race at min(G, need), the consistency-cap exit by the "
            "same race at its cap level, **both at R = the R the trade was read at** (`lt[\"rr\"]`), **never "
            "`rr_used` on that path**",                                                                    # 3
            "**at the contracts held, as the engine charges them** (D-324",                                # 4
            "`be_open` is the move bar's **end** index, s + 1 on Stage 2's bar-end clock",                  # 5
            "a missing bar is voided only by Q-197's pinned calendar, never by data",                       # 5
            "the trades where the vendored bar differs from s + 1 are counted beside",                     # 5
            "**a `be_open` at or after the limit means the trade has no move**",                           # 5
            "**refused**: P-16's abandon leaves (risk 0) take no trade; **no `log_rr` fallback**",          # 6
            "**read from bars closed at or before the alert only**"):                                      # 8
        assert phrase in s7, phrase
    assert "keeps its exit's law (the terminal-state map), and the share of such trades" not in s7
    s16 = _flat(_section(text, 16))
    assert "on the race arm **`u` and `mae` are not applicable**, never the historical trade's" in s16      # 7
    fp = _deps(text)["the firm path"]
    assert "**the firm path's baseline-mode laws as `BUILD_FIRMPATH_c2_2026-11-21` rules them**" in fp
    assert "**both breakeven\n  shares**" in text or "**both breakeven shares**" in _flat(_section(text, 12))
