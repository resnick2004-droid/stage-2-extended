"""Q-210: the declaration lint -- a light, mechanical check of a declaration's form, run in seconds by its author
before any review, so that form refusals stop costing review cycles (the gatekeeper's note: "machine check: none
exists for F-files (or H-files)", `docs/reviews/GK_H3_c2_2026-11-22.md` l.3).

    python scripts/decl_lint.py prereg/F-NN_<slug>.md
    python scripts/decl_lint.py <file> --rev f454d8d --as prereg/H3_three_way.md --template <path>

It reads one declaration and the files it cites, and changes nothing. **Exit 0: clean** (warnings may be printed).
**Exit 1: a numbered list of problems**, each `path:line: [rule] message`; errors first, then warnings. Exit 2: the
lint could not run (a bad argument, a file it cannot read).

The checks, each derived from a refusal or a review on record (the hand-back of Q-210 gives each source's line):

1. `form.*` -- **pin-time form**, for a file named for pinning (`F-NN_`, `RD-NN_`, `H<n>_`; or `--pin`): the title,
   status and header true of the pinned file (no "DRAFT", "a draft", "not pinned", "this draft", "this commit": E-075
   (1), as RD-02 l.92 lists it), no future-tense pinning sentence ("to be pinned", "will be pinned", "pinned only
   after"; the gatekeeper's item 1 on H3), nothing unresolved (`TBD`, `TODO`, `k = ?`, a lone `?` value, a template
   placeholder `<...>` or a bare `F-XX`).
2. `xref.*` -- **cross-references resolve**: a template's section cited ("template v3's section 7", "the family
   template (section 14 item 4)", "§5") exists in that template, holds the item cited, holds the label the text names
   with it (R-10 cited at section 7 fails when R-10 is defined in section 5: the gatekeeper's refusal item 1 on H3), and a
   template cited "as pinned" has its pin row; every `E-NNN` is a row of master's `DECISIONS.md`; every commit sha names
   a commit reachable from HEAD (or from `--rev`); every cited path exists; every LF sha256 cited beside a path is that
   file's.
3. `count.*` -- **counts written as a product and a number** (the template's "`k_cells` = <the product of the cells'
   factors, written as a product and a number>"; the gatekeeper's refusal item 3 on H3): in the count sections and on
   every `k_cells` line, a product with no number, a product whose factor is not a number written there, a product
   that does not equal its number, and a `k_cells` number with no product.
4. `seed.*` -- **seeds**: no literal of any declared seed block in a file outside that block's declared uses. The
   blocks and their uses are read from **the seed guards' own constants** (every `tests/`, `scripts/` or `extended/`
   module defining `SEED_BLOCK`, with its `DECLARED_USES`, `DERIVED_USES` and path constants), evaluated without
   importing the module; nothing is copied here.
5. `token.*` -- **tokens**: every `identity-holds:`, `heldout-finalists:`, `heldout-window:`, `heldout-verdict:`,
   `heldout-read:`, `heldout-void:`, `heldout-closed:` or `go:` string is in the grammar `extended/identity_tokens.py`
   and `extended/reader.py` accept (`go:` and `heldout-closed:` in the design-search template's form, which no merged
   code parses yet), with placeholders only where a value belongs; a real token is only ever the first text of a
   decision row's third cell.
6. `date.*` -- **held-out and confirmation dates**: no date of the held-out years (2024-01-02 to 2026-07-16) outside a
   never-read or refusal statement, unless the declaration carries the reader's `Judged-block reads:` line (the
   market's held-out declaration, or a family of the older judged-block form); no date from 2026-07-17 except as a
   refusal or the confirmation window's declaration (a purchase, for a carried design only).
7. `figure.typed` -- **typed figures**, a warning only: a decimal with three or more significant digits or a
   percentage, outside fenced blocks, not found in the charter, the measures or the templates, and on no sentence
   labelled as a rule value, a seed, a declared parameter, a test's known answer or a cited review measurement.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extended import identity_tokens as IT  # noqa: E402  (the one parser of the identity tokens, Q-110)
from extended import reader as RD  # noqa: E402            (the held-out token grammar and the judged-block line)

ERROR, WARNING = "error", "warning"

#: a file named for pinning (the reader's `DECLARATION_PATH`, the H-files of E-208, a playbook declaration)
PIN_NAME = re.compile(r"^(?:(?:F|RD)-\d+_[^/]*\.md|H\d+_[^/]*\.md|[^/]*_playbook\.json)$")
DRAFT_NAME = re.compile(r"^(?:DRAFT_|TEMPLATE_)")

# --- 1. pin-time form ------------------------------------------------------------------------------------------------
#: words that make a head (title, status, header table) a draft's (E-075 (1), RD-02 l.92's list)
HEAD_DRAFT = re.compile(r"(?-i:\bDRAFT\b)(?![_ ]file| name)|\(draft\)|\ba draft\b|\bnot pinned\b|\bthis draft\b"
                        r"|\bthis commit\b|\*\*Status:[^*\n]*\bdraft\b|\bfor the red team'?s (?:re-?)?read\b",
                        re.IGNORECASE)
#: a quoted word list ("DRAFT", "this draft") names the forbidden words; it is not the file's own status
QUOTED = re.compile(r"\"[^\"\n]{1,40}\"|`[^`\n]*`|\u201c[^\u201d\n]{1,40}\u201d")
#: anywhere in the text: a draft's self-reference, a future-tense pinning sentence, an unresolved value
BODY_FORM = (
    (re.compile(r"\bthis draft\b|\(a draft\)|\*\*Status: a draft", re.IGNORECASE), "a draft's self-reference"),
    (re.compile(r"\b(?:to|will|shall|would) be pinned\b|\bis to be pinned\b|\bpinned only after\b"
                r"|\bis pinned (?:\([^)]{0,120}\) )?only after\b"
                r"|\b(?:once|when|until) (?:this (?:file|text|declaration|draft)|it) is pinned\b"
                r"|\b(?:this (?:file|text|declaration)|it) is not (?:yet )?pinned\b|\bnot yet pinned\b",
                re.IGNORECASE), "a future-tense pinning sentence"),
    (re.compile(r"\bTBD\b|\bTODO\b|\bFIXME\b"), "an unresolved marker"),
    (re.compile(r"\bk\s*=\s*\?"), "an unresolved k (`k = ?`)"),
    (re.compile(r"(?:(?<=[=:|])|(?<=[=:|] ))\s*\?\s*(?=$|[|,;)])"), "an unresolved value (`?`)"),
    (re.compile(r"<\.\.\.>"), "a template placeholder left (`<...>`)"),
)
BARE_FXX = re.compile(r"(?<![\w`-])F-XX(?![\w`])")
TEMPLATE_PROSE = re.compile(r"<(?![a-z]+>)[A-Za-z][^<>|`\n]{12,}>")       # `<What the search looks for ...>`

# --- 2. cross-references ---------------------------------------------------------------------------------------------
TEMPLATE_CITE = re.compile(
    r"(?P<tpl>`[^`\n]*TEMPLATE[^`\n]*`|(?<![\w'])(?:[\w'-]+[ -]){0,2}template\b(?:\s+(?:text\s+)?v\d+)?)"
    r"(?P<gap>[^.;|\n]{0,40}?)"
    r"(?:\bsection|§)\s*(?P<num>\d+)(?:\.(?P<sub>\d+))?(?:\s+item\s+(?P<item>\d+))?", re.IGNORECASE)
LABEL = re.compile(r"(?<![\w-])([A-Za-z]{1,2}-\d{1,2}'?)(?![\w-])")
NOT_LABEL = re.compile(r"^(?:E|D|Q|F|P|RD|H|U|S|T|L|A|C|R|W|K)-\d+$")     # rows, ids and cells, never a topic alone
TOPIC_LABEL = re.compile(r"^[A-Za-z]{1,2}-\d{1,2}'?$")
E_ROW = re.compile(r"(?<![\w-])E-(\d{3})(?![\w-])")
#: words before a sha that say it is one (an abbreviation may be all letters: `ceedcbb`)
COMMIT_CONTEXT = re.compile(r"(?:\bcommits?|\bat|\bsha|\bbuild|\bmerged?|\bof|wt/[\w-]+|`)\s*`?$", re.IGNORECASE)
SHA = re.compile(r"(?<![\w./+-])([0-9a-f]{7,40})(?![\w+-])")
BACKTICK = re.compile(r"`([^`\n]+)`")
PATH_EXT = (".md", ".py", ".yaml", ".yml", ".csv", ".json", ".jsonl", ".txt", ".sha256", ".toml", ".parquet", ".ini",
            ".cfg", ".ps1", ".sh")
PATH_PREFIXES = ("", "vendor/stage2/", "vendor/stage2/scripts/", "vendor/stage2/vendor/propsim/", "extended/",
                 "scripts/", "tests/", "prereg/", "docs/", "identity/", "config/")
#: code a declaration may name before it exists: the build follows the pin (the family template, section 17)
BUILD_DIRS = ("extended/", "scripts/", "tests/", "identity/")
#: the licensed bars and atlas live under these: never read here (only named as cited, never opened)
DATA_PATHS = ("vendor/stage2/data/", "data/")
MADE_LATER = re.compile(r"\b(?:writ\w*|wrote|build\w*|built|creat\w*|adds?|added|new|future|later|produc\w*|outputs?"
                        r"|generat\w*|to be|will|once|when)\b", re.IGNORECASE)
SHA256_CITE = re.compile(r"`(?P<path>[^`\s]+)`(?P<mid>[^`]{0,80}?)sha256[^`]{0,24}?"
                         r"`(?P<hex>[0-9a-f]{64}|[0-9a-f]{6,}(?:\.\.\.|…)[0-9a-f]{3,})`", re.DOTALL)
TEMPLATE_PIN = r"`prereg/{name}` sha256 `([0-9a-f]{{64}})`"

# --- 3. counts -------------------------------------------------------------------------------------------------------
COUNT_HEADING = re.compile(r"^#{2,4} .*\b(?:count|counting|cells)\b", re.IGNORECASE)
OP = re.compile(r"\s[x×]\s")
NUMERIC_EXPR = re.compile(r"(?<![\w.])(\(?\d[\d,]*\)?(?:\s*[x×*+]\s*\(?\d[\d,]*\)?)+)\s*=\s*\**\s*(\d[\d,]*)(?!\d|\.\d)")
K_CELLS_NUMBER = re.compile(r"k_cells`?\)?\s*(?:=|\||:|\*\*)+\s*\**\s*(\d+)")
SPELLED = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}

# --- 4. seeds --------------------------------------------------------------------------------------------------------
SEED_LIT = re.compile(r"(?<![\w.-])(2026\d{4})(?![\w-]|\.\d)")
SEED_ROW = re.compile(r"^\|\s*`?(2026\d{4})`?\s*\|", re.MULTILINE)
#: the seed guards are tests (`grep -rl seed_block tests`); a `SEED_BLOCK` in code is its block's owner, a declared use
GUARD_DIRS = ("tests",)
OWNER_DIRS = ("scripts", "extended")
#: files that cite seeds by their role without drawing them: the decision log and the reviews
SEED_RECORD = ("DECISIONS.md", "docs/reviews/")
TEXT_EXT = (".md", ".py", ".yaml", ".yml", ".csv", ".json", ".jsonl", ".txt", ".toml", ".cfg", ".ini", ".sha256")

# --- 5. tokens -------------------------------------------------------------------------------------------------------
_HO_TAIL = r"(?= -- [^\s|]| \|)"
#: the design-search template's go row (text v3, step 4; G-1, E-259) and closing row (step 4; the held-out template's
#: closed list), in the reader's positional form; no merged code parses either yet (wt/wt-lit's test holds `GO_TOKEN`)
GO = re.compile(r"\| (?P<row>E-\d+) \| \d{4}-\d{2}-\d{2} \| go: (?P<decl>F-\d+) @ (?P<sha>[0-9a-f]{64})" + _HO_TAIL)
CLOSED = re.compile(r"\| (?P<row>E-\d+) \| \d{4}-\d{2}-\d{2} \| heldout-closed: (?P<decl>F-\d+) @ (?P<sha>[0-9a-f]{64})"
                    r" -- (?P<cause>[a-z][a-z-]*) -- (?=[^\s|])")
GO_LIKE = re.compile(r"(?<![\w-])go\s*[:=]\s*`?(?=F-|<)", re.IGNORECASE)
CLOSED_LIKE = re.compile(r"held[-_ ]?out[-_ ]?closed\s*[:=]", re.IGNORECASE)
PLACEHOLDER_SUBS = (
    (re.compile(r"\bE-NNN\b"), "E-999"),
    (re.compile(r"<YYYY-MM-DD>|YYYY-MM-DD|<date>"), "2026-01-01"),
    (re.compile(r"\bF-(?:NN|XX|HT)\b"), "F-99"),
    (re.compile(r"<[^<>]*sha[^<>]*>"), "0" * 64),
    (re.compile(r"<(?:MARKET|market)>"), "NQ"),
    (re.compile(r"<(?:first|start)>"), "2026-01-01"),
    (re.compile(r"<(?:last|end)>"), "2026-01-02"),
    (re.compile(r"<(?:cause)>"), "withdrawn"),
    (re.compile(r"<(?:id)>|\bQ-nn\b"), "Q-1"),
    (re.compile(r"<x>"), "x"),
    (re.compile(r"<[^<>]*>"), "text"),
)

# --- 6. dates --------------------------------------------------------------------------------------------------------
DATE = re.compile(r"(?<![\w-])(20\d\d)-(\d\d)-(\d\d)(?![\w-])")
HELD_OUT = (date(2024, 1, 2), date(2026, 7, 16))
CONFIRMATION = date(2026, 7, 17)
NEVER = re.compile(r"never(?: be)? read|not read|unread|read by no|reads? no\b|never|refus\w*|not on disk|sealed?\b"
                   r"|forbid\w*|withheld|held back", re.IGNORECASE)
READ_WORD = re.compile(r"\breads?\b|\breplay(?:s|ed)?\b|\bloads?\b", re.IGNORECASE)
CONFIRMATION_DECL = re.compile(r"confirmation", re.IGNORECASE)
#: a date of market data is named with one of these; a firm's terms or a rule's verification date is not
DATA_WORD = re.compile(r"\bNQ\b|\bbars?\b|\bsessions?\b|\bdata\b|\bwindow\b|\bwalks?\b|\batlas\b"
                       r"|\bdevelopment\b|\bconfirmation\b|\breplay\w*|\bheld-out\b|\bjudged\b|\bblock\b|\bspan\b",
                       re.IGNORECASE)
NEGATION = re.compile(r"\bno\b|\bnot\b|\bnor\b|\bnone\b|does not reach|\bbefore\b", re.IGNORECASE)
RESERVE = re.compile(r"\breserved?\b|windows\.yaml", re.IGNORECASE)
CONFIRMATION_TERMS = re.compile(r"purchase|carried|registered|operator", re.IGNORECASE)
RANGE = re.compile(r"(20\d\d-\d\d-\d\d)\s*(?:to|-|–|until)\s*(20\d\d-\d\d-\d\d)")

# --- 7. typed figures ------------------------------------------------------------------------------------------------
DECIMAL = re.compile(r"(?<![\w.-])(\d+\.\d+)(?![\w]|\.\d)")
PERCENT = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?) ?%")
FIGURE_LABEL = re.compile(
    r"rules(?:_extended)?\.yaml|\bverified\b|\bD-\d+|\bseeds?\b|known answer|\btoy\b|\btest_\w+|docs/reviews/"
    r"|\bred team\b|\b(?:MINOR|NOTE|MATERIAL)-\d|\bmeasured\b|\bfixed\b|\bdeclared\b|\bparameter|\bdenial\b"
    r"|\brule value|\bstop band\b|\blevel\b|\btolerance\b|\bstress\b|\bplaceholder\b|\bstylised\b|\bknown\b"
    r"|\bat (?:most|least)\b|\bat or (?:above|below)\b|\bwithin\b|\babove\b|\bbelow\b|\bthreshold\b|\bcap\b"
    r"|\bmargin\b|\bledger\b|`[A-Za-z_][\w.]*\.[A-Z_]{2,}`|`[A-Z][A-Z0-9_]{2,}`|`\w+\.\w+\.\w+`", re.IGNORECASE)
#: a figure with a unit of contract arithmetic or time: a bracket, a size, a span
UNIT_AFTER = re.compile(r"^(?:-| )?(?:points?|ticks?|pts|contracts?|minutes?|sessions?|days?|hours?|R\b)",
                        re.IGNORECASE)
#: a table row answering a review's finding (its key a finding id): the row cites the review's measurement
FINDING_ROW = re.compile(r"^\|\s*\**(?:[A-Za-z]{1,3}\d?-\d+|gk \d|v\d \w-\d|sc \w+-\d)")
SECTION_NUMBER = re.compile(r"(?:\b(?:section|sections|CHARTER|§|item|rule|step|table)\s*|\b[A-Z][\w-]* )(\d+\.\d+)")


@dataclass(frozen=True)
class Problem:
    severity: str
    path: str
    line: int
    rule: str
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: [{self.rule}] {self.message}"


# =================================================================================================== the trees

def _git(repo: Path, *args: str, check: bool = False, stdin: str | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", input=stdin, timeout=120)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


class Tree:
    """The repository's files as the lint resolves citations: the working tree at `repo`, or the tree of commit `rev`
    (read with git, nothing checked out). Licensed data paths are never read."""

    def __init__(self, repo: Path, rev: str | None = None):
        self.repo, self.rev = repo, rev
        self._cache: dict[str, bytes | None] = {}
        if rev:
            out = _git(repo, "ls-tree", "-r", "--name-only", rev, check=True).stdout
        else:
            out = _git(repo, "ls-files").stdout + _git(repo, "ls-files", "-o", "--exclude-standard").stdout
        self.names = {n for n in out.splitlines() if n}
        self.dirs = {str(PurePosixPath(n).parent) for n in self.names}
        for d in list(self.dirs):
            p = PurePosixPath(d)
            self.dirs.update(str(q) for q in p.parents)
        self.by_base: dict[str, list[str]] = {}
        for n in self.names:
            self.by_base.setdefault(n.rsplit("/", 1)[-1], []).append(n)

    def head(self) -> str:
        return self.rev or "HEAD"

    def exists(self, rel: str) -> bool:
        rel = rel.rstrip("/")
        if rel in self.names or rel in self.dirs:
            return True
        return not self.rev and (self.repo / rel).exists()

    def read(self, rel: str) -> bytes | None:
        if rel in self._cache:
            return self._cache[rel]
        data: bytes | None = None
        if any(rel.startswith(d) for d in DATA_PATHS):
            data = None
        elif self.rev:
            r = subprocess.run(["git", "show", f"{self.rev}:{rel}"], cwd=str(self.repo), capture_output=True,
                               timeout=120)
            data = r.stdout if r.returncode == 0 else None
        else:
            p = self.repo / rel
            data = p.read_bytes() if p.is_file() else None
        self._cache[rel] = data
        return data

    def text(self, rel: str) -> str | None:
        b = self.read(rel)
        return None if b is None else b.decode("utf-8", errors="replace").replace("\r\n", "\n")

    def read_at(self, commit: str, rel: str) -> bytes | None:
        r = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=str(self.repo), capture_output=True, timeout=120)
        return r.stdout if r.returncode == 0 else None


def sha256_lf(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


# =================================================================================================== the text

@dataclass
class Text:
    """A declaration's LF text, its lines, which lines sit in fenced blocks, and its sections by heading."""
    rel: str
    body: str
    lines: list[str] = field(init=False)
    fenced: list[bool] = field(init=False)
    starts: list[int] = field(init=False)

    def __post_init__(self) -> None:
        self.lines = self.body.split("\n")
        self.fenced, inside = [], False
        for line in self.lines:
            opener = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            if opener:
                self.fenced.append(True)
                inside = not inside
                continue
            self.fenced.append(inside)
        self.starts, pos = [], 0
        for line in self.lines:
            self.starts.append(pos)
            pos += len(line) + 1

    def line_of(self, offset: int) -> int:
        lo, hi = 0, len(self.starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    def head_end(self) -> int:
        """The line index (0-based) where the head ends: the first `## ` heading or `---` rule after the title."""
        for i, line in enumerate(self.lines[1:], start=1):
            if line.startswith("## ") or line.strip() == "---":
                return i
        return len(self.lines)

    def unit(self, i: int) -> tuple[int, str]:
        """(the 0-based first line, the text) of the unit holding line `i`: its table row, its list item, or its
        paragraph, joined with spaces."""
        line = self.lines[i]
        if line.lstrip().startswith("|") or line.startswith("#"):
            return i, line
        a = i
        while a > 0 and self.lines[a - 1].strip() and not self._starts_unit(a):
            a -= 1
        b = i
        while b + 1 < len(self.lines) and self.lines[b + 1].strip() and not self._starts_unit(b + 1):
            b += 1
        return a, " ".join(x.strip() for x in self.lines[a:b + 1])

    def _starts_unit(self, j: int) -> bool:
        s = self.lines[j].lstrip()
        return bool(s.startswith(("|", "#", "- ", "* ", "> ")) or re.match(r"\d+\. ", s) or self.fenced[j])

    def sentence(self, i: int, col: int) -> str:
        """The sentence of line `i` holding column `col` (a table row is its own sentence)."""
        a, text = self.unit(i)
        if a == i and self.lines[i].lstrip().startswith("|"):
            cells = self.lines[i].split("|")
            key = next((c for c in cells if c.strip()), "")
            pos = 0
            for c in cells:
                if pos <= col <= pos + len(c):
                    return c if c is key else f"{key} | {c}"
                pos += len(c) + 1
            return self.lines[i]
        offset = sum(len(x.strip()) + 1 for x in self.lines[a:i]) + max(0, col - (len(self.lines[i]) -
                                                                              len(self.lines[i].lstrip())))
        bounds = [0] + [m.end() for m in re.finditer(r"(?<=[.])\s+(?=[A-Z*(`\-])", text)] + [len(text)]
        for s, e in zip(bounds, bounds[1:]):
            if s <= offset < e:
                return text[s:e]
        return text

    def sections(self) -> list[tuple[str, str, int, int]]:
        """(number, heading, first line, last line) of every `## N.` heading, 0-based lines."""
        out = []
        heads = [(i, m) for i, line in enumerate(self.lines)
                 if not self.fenced[i] and (m := re.match(r"^##\s+(?:§\s*)?([0-9A-Z]+)\.?\s+(.*)$", line))]
        for k, (i, m) in enumerate(heads):
            end = heads[k + 1][0] - 1 if k + 1 < len(heads) else len(self.lines) - 1
            out.append((m.group(1), m.group(2).strip(), i, end))
        return out


# =================================================================================================== the lint

class Lint:
    def __init__(self, decl: Path, tree: Tree, rel: str | None = None, templates: Iterable[Path] = (),
                 decisions: str | None = None, pin: bool | None = None):
        self.tree = tree
        raw = decl.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
        if rel is None:
            try:
                rel = decl.resolve().relative_to(tree.repo.resolve()).as_posix()
            except ValueError:
                rel = f"prereg/{decl.name}"
        self.rel = rel
        self.shown = decl.as_posix()
        self.text = Text(rel, raw)
        self.problems: list[Problem] = []
        self.decisions = decisions if decisions is not None else self._master_decisions()
        self.rows = set(re.findall(r"^\| (E-\d+) \|", self.decisions, re.MULTILINE))
        name = PurePosixPath(rel).name
        self.pin = pin if pin is not None else bool(PIN_NAME.match(name) and not DRAFT_NAME.match(name))
        self.templates = self._templates(templates)
        self._master: Tree | None = None

    def master(self) -> Tree | None:
        """master's tree: a cited file or commit there is in the tree the declaration is merged and pinned into."""
        if self._master is None and self.tree.rev != "master":
            try:
                self._master = Tree(self.tree.repo, "master")
            except RuntimeError:
                self._master = None
        return self._master

    # -- inputs
    def _master_decisions(self) -> str:
        for ref in ("master", "HEAD"):
            r = _git(self.tree.repo, "show", f"{ref}:DECISIONS.md")
            if r.returncode == 0:
                return r.stdout.replace("\r\n", "\n")
        p = self.tree.repo / "DECISIONS.md"
        return p.read_text(encoding="utf-8").replace("\r\n", "\n") if p.exists() else ""

    def _templates(self, extra: Iterable[Path]) -> dict[str, Text]:
        out: dict[str, Text] = {}
        for rel in sorted(self.tree.names):
            if re.fullmatch(r"prereg/TEMPLATE_[^/]+\.md|vendor/stage2/prereg/(?:FAMILY_)?TEMPLATE\.md", rel):
                t = self.tree.text(rel)
                if t is not None:
                    out[PurePosixPath(rel).name] = Text(rel, t)
        for p in extra:
            out[p.name] = Text(f"prereg/{p.name}", p.read_bytes().decode("utf-8").replace("\r\n", "\n"))
        return out

    def add(self, severity: str, line: int, rule: str, message: str) -> None:
        self.problems.append(Problem(severity, self.shown, line, rule, message))

    def own_lines(self) -> Iterable[tuple[int, str]]:
        for i, line in enumerate(self.text.lines):
            if not self.text.fenced[i]:
                yield i, line

    def run(self) -> list[Problem]:
        for check in (self.check_form, self.check_xref, self.check_counts, self.check_seeds, self.check_tokens,
                      self.check_dates, self.check_figures):
            check()
        seen, out = set(), []
        for p in sorted(self.problems, key=lambda p: (p.severity != ERROR, p.line, p.rule)):
            if (p.line, p.rule, p.message) not in seen:
                seen.add((p.line, p.rule, p.message))
                out.append(p)
        return out

    # ------------------------------------------------------------------------------------------ 1. pin-time form
    def check_form(self) -> None:
        if not self.pin:
            return
        head = self.text.head_end()
        for i, raw in self.own_lines():
            line = QUOTED.sub(lambda m: " " * len(m.group(0)), raw)       # a quoted word is named, not used
            if i < head and not line.lstrip().startswith("|") or i == 0:
                for m in HEAD_DRAFT.finditer(line):
                    self.add(ERROR, i + 1, "form.head", f"the head is a draft's: {m.group(0)!r} (E-075 (1): the "
                             "title, status and header true of the pinned file)")
            elif i < head and re.match(r"^\|\s*(?:status|state)\s*\|", line, re.IGNORECASE):
                for m in HEAD_DRAFT.finditer(line):
                    self.add(ERROR, i + 1, "form.head", f"the header's status is a draft's: {m.group(0)!r} (E-075 (1))")
            for rx, what in BODY_FORM:
                for m in rx.finditer(line):
                    self.add(ERROR, i + 1, "form.phrase", f"{what}: {m.group(0).strip()!r} in a file named for pinning")
            a, unit = self.text.unit(i)
            if a == i and unit != raw:                  # a sentence wrapped over lines: read the paragraph whole
                joined = QUOTED.sub(lambda m: " " * len(m.group(0)), unit)
                ends = [0]
                for x in self.text.lines[a:]:
                    ends.append(ends[-1] + len(x.strip()) + 1)
                    if ends[-1] > len(joined):
                        break
                for rx, what in BODY_FORM:
                    for m in rx.finditer(joined):
                        k = next(j for j, e in enumerate(ends[1:]) if m.start() < e)
                        if m.end() > ends[k + 1] - 1:   # it crosses a line end: no single line holds it
                            self.add(ERROR, a + k + 1, "form.phrase", f"{what}: {m.group(0).strip()!r} in a file "
                                     "named for pinning")
            for m in BARE_FXX.finditer(line):
                self.add(ERROR, i + 1, "form.placeholder", "the placeholder F-XX left (the gatekeeper replaces it at "
                         "the pin)")
            bare = BACKTICK.sub(lambda m: " " * len(m.group(0)), line)
            for m in TEMPLATE_PROSE.finditer(bare):
                self.add(ERROR, i + 1, "form.placeholder", f"a template placeholder left: {m.group(0)[:60]!r} (a "
                         "section left as the template wrote it is a gap the gatekeeper refuses)")

    # ------------------------------------------------------------------------------------------ 2. cross-references
    def check_xref(self) -> None:
        self._template_citations()
        self._rows()
        self._commits()
        self._paths()
        self._sha256s()

    def _which_template(self, phrase: str) -> tuple[str | None, str]:
        p = phrase.strip("`").lower()
        if "template_" in p or p.endswith("template.md"):
            name = p.rsplit("/", 1)[-1]
            for k in self.templates:
                if k.lower() == name:
                    return k, phrase
            return None, f"{phrase} (no such template file)"
        v = re.search(r"\bv(\d+)\b", p)
        if v:
            for k, t in self.templates.items():
                if re.search(rf"\*\*Text v{v.group(1)}\b", t.body):
                    return k, phrase
            return None, f"{phrase} (no template whose text is v{v.group(1)}; pass it with --template)"
        for key, name in (("design", "TEMPLATE_design_search.md"), ("held", "TEMPLATE_heldout_test.md"),
                          ("family", "TEMPLATE_family.md"), ("stage 2", "TEMPLATE.md")):
            if key in p:
                return (name if name in self.templates else None), phrase
        body = self.text.body
        if RD.DESIGN_SEARCH_MARKER in body:
            return ("TEMPLATE_design_search.md" if "TEMPLATE_design_search.md" in self.templates else None), phrase
        if RD.HELDOUT_MARKER in body:
            return ("TEMPLATE_heldout_test.md" if "TEMPLATE_heldout_test.md" in self.templates else None), phrase
        head = "\n".join(self.text.lines[:self.text.head_end()])
        m = re.search(r"prereg/(TEMPLATE_[^`]+\.md)", head)
        if m and m.group(1) in self.templates:
            return m.group(1), phrase
        return None, f"{phrase} (which template is not said)"

    def _template_citations(self) -> None:
        for i, line in self.own_lines():
            for m in TEMPLATE_CITE.finditer(line):
                tpl = m.group("tpl")
                if re.search(r"\b(?:this|our|its own)\b", tpl, re.IGNORECASE):
                    continue
                name, shown = self._which_template(tpl)
                num, item = m.group("num"), m.group("item")
                where = f"{shown.strip()} section {num}"
                if name is None:
                    self.add(WARNING, i + 1, "xref.template-unknown", f"{where}: the template cannot be resolved")
                    continue
                t = self.templates[name]
                secs = {n: (h, a, b) for n, h, a, b in t.sections()}
                if num not in secs:
                    self.add(ERROR, i + 1, "xref.template-section", f"{where}: {name} has no section {num} "
                             f"(its sections: {', '.join(secs)})")
                    continue
                heading, a, b = secs[num]
                sec_body = "\n".join(t.lines[a:b + 1])
                if item and not re.search(rf"(?m)^\s*{item}\.\s", sec_body):
                    self.add(ERROR, i + 1, "xref.template-item", f"{where} item {item}: {name} section {num} "
                             f"(\"{heading}\") has no item {item}")
                self._topic(i, line, m, name, t, num, heading, sec_body)
                tail = line[m.end():m.end() + 40]
                if re.match(r"[^.;|]{0,12}\bas pinned\b", tail):
                    if not re.search(TEMPLATE_PIN.format(name=re.escape(name)), self.decisions):
                        self.add(ERROR, i + 1, "xref.template-unpinned", f"{where} \"as pinned\": no decision row "
                                 f"pins `prereg/{name}` by its sha256 (the text would govern by a rule that can "
                                 "still change)")

    def _topic(self, i: int, line: str, m: re.Match, name: str, t: Text, num: str, heading: str,
               sec_body: str) -> None:
        """The label the text names with the citation (before it in the same sentence or cell) must be in the cited
        section -- at its definition when the template defines it; a quoted heading must be the section's."""
        lo = max(0, m.start() - 250)
        before = line[lo:m.start()]
        cut = before.rfind(". ")
        before = before[cut + 1:] if cut >= 0 else before
        if line.lstrip().startswith("|"):                   # a table row: its key cell names the topic too
            before = before[before.rfind("|") + 1:] + " " + next((c for c in line.split("|") if c.strip()), "")
        labels = [x for x in LABEL.findall(before) if TOPIC_LABEL.match(x) and not NOT_LABEL.match(x.rstrip("'"))
                  or x.startswith("R-")]
        for lab in dict.fromkeys(labels):
            if lab not in t.body:
                continue
            defined = self._definition(t, lab)
            ok = (defined == num) if defined else (lab in sec_body)
            if not ok:
                where = f"section {defined}" if defined else "elsewhere"
                hd = dict((n, h) for n, h, _, _ in t.sections()).get(defined, "")
                self.add(ERROR, i + 1, "xref.template-topic", f"{lab} is cited at {name} section {num} "
                         f"(\"{heading}\"), but {lab} is defined in {where}" + (f" (\"{hd}\")" if hd else ""))
        q = re.match(r"\s*[,(]?\s*[\"'“*_]+([^\"'”*_]{6,80})[\"'”*_]", line[m.end():])
        if q:
            want = set(re.findall(r"[a-z]{4,}", q.group(1).lower()))
            have = set(re.findall(r"[a-z]{4,}", heading.lower()))
            if want and len(want & have) < max(1, len(want) // 2):
                self.add(ERROR, i + 1, "xref.template-topic", f"section {num} of {name} is \"{heading}\", not "
                         f"\"{q.group(1)}\"")

    @staticmethod
    def _definition(t: Text, lab: str) -> str | None:
        pat = re.compile(rf"^\s*(?:[-*]|\d+\.)?\s*\*\*{re.escape(lab)}[:.\s]|^#+ .*\b{re.escape(lab)}\b")
        for n, _, a, b in t.sections():
            for line in t.lines[a:b + 1]:
                if pat.search(line):
                    return n
        return None

    def _rows(self) -> None:
        seen = set()
        for i, line in self.own_lines():
            for m in E_ROW.finditer(line):
                rid = f"E-{m.group(1)}"
                if rid not in self.rows and rid not in seen:
                    seen.add(rid)
                    self.add(ERROR, i + 1, "xref.row", f"{rid} is not a row of master's DECISIONS.md")

    def _commits(self) -> None:
        found: dict[str, tuple[int, str]] = {}
        for i, line in self.own_lines():
            for m in SHA.finditer(line):
                s = m.group(1)
                if len(s) not in range(7, 13) and len(s) != 40:
                    continue
                pre = line[max(0, m.start() - 24):m.start()]
                if not re.search(r"\d", s) and not COMMIT_CONTEXT.search(pre):
                    continue                    # an all-letter word is a sha only where the text calls it one
                if not re.search(r"[a-f]", s):
                    continue
                post = line[m.end():m.end() + 3]
                if re.search(r"sha256|sha-256|hash\b", pre, re.IGNORECASE) or post.startswith(("...", "…")) \
                        or pre.endswith(("...", "…")):
                    continue
                found.setdefault(s, (i, line[max(0, m.start() - 60):m.start()]))
        if not found:
            return
        batch = _git(self.tree.repo, "cat-file", "--batch-check", stdin="\n".join(found) + "\n").stdout.splitlines()
        for (s, (i, before)), reply in zip(found.items(), batch):
            if reply.endswith("missing") or "ambiguous" in reply:
                if "ambiguous" in reply:
                    self.add(WARNING, i + 1, "xref.commit", f"{s} is an ambiguous abbreviation; write more of it")
                else:
                    self.add(ERROR, i + 1, "xref.commit", f"{s} names no object in this repository")
                continue
            full, kind = reply.split()[:2]
            if kind == "blob":                  # a file's git blob id beside its path (`path` `<blob>`)
                p = re.findall(r"`([^`\s]+)`\s*$", before)
                rel = self._resolve(p[-1])[0] if p else None
                if rel is not None:
                    blob = _git(self.tree.repo, "rev-parse", f"{self.tree.head()}:{rel}").stdout.strip()
                    if blob and blob != full:
                        self.add(ERROR, i + 1, "xref.commit", f"{s} is a blob, but `{rel}` in {self.tree.head()} is "
                                 f"{blob[:12]}")
                continue
            if kind != "commit":
                self.add(WARNING, i + 1, "xref.commit", f"{s} names a {kind}, not a commit")
                continue
            heads = [self.tree.head()] + (["master"] if self.master() is not None else [])
            if any(_git(self.tree.repo, "merge-base", "--is-ancestor", full, h).returncode == 0 for h in heads):
                continue
            branches = [b.strip().lstrip("*+ ").strip() for b in
                        _git(self.tree.repo, "branch", "-a", "--contains", full).stdout.splitlines()]
            named = [b for b in branches if b.split("/", 1)[-1] in before or b in before]
            if named:
                self.add(WARNING, i + 1, "xref.commit", f"{s} is reachable from {named[0]} (named) but not from "
                         f"{self.tree.head()}: it is lost if that branch goes")
            else:
                self.add(ERROR, i + 1, "xref.commit", f"{s} is not reachable from {self.tree.head()}"
                         + (f" (only from {', '.join(branches[:3])})" if branches else ""))

    def _resolve(self, token: str) -> tuple[str | None, bool]:
        """(the repository path a cited token names, whether it is path-shaped at all)."""
        t = token.strip().rstrip(".,;:)").lstrip("(")
        t = re.sub(r":\d+(?:-\d+)?$", "", t)
        t = re.sub(r"^[\w./-]+:(?=[\w.-]+/)", "", t)            # `HEAD:extended/x.py`, `<rev>:<path>`
        if not t or any(c in t for c in "<>*?{}$ ") or "://" in t or t.startswith(("-", "_", "~", "%", ".")) \
                or re.search(r"(?<![A-Za-z])(?:NN|XX|nn|xx)(?![A-Za-z])", t) or "\\" in t:
            return None, False
        has_ext = t.lower().endswith(PATH_EXT) and not t.rsplit("/", 1)[-1].startswith(".")
        if not (has_ext or (t.endswith("/") and "/" in t[:-1])):
            return None, False
        if "/" not in t:
            if t in self.tree.by_base or self.tree.exists(t):
                return self.tree.by_base.get(t, [t])[0], True
            return None, True
        for tree in (self.tree, self.master()):
            for pre in PATH_PREFIXES:
                if tree is not None and tree.exists(pre + t):
                    return pre + t, True
        if any(t.startswith(d) for d in DATA_PATHS):
            return t, True
        return None, True

    def _paths(self) -> None:
        seen, missing = set(), []
        for i, line in self.own_lines():
            for m in BACKTICK.finditer(line):
                tok = m.group(1)
                rel, shaped = self._resolve(tok)
                if not shaped or rel is not None or tok in seen or tok.rstrip("/") == self.rel:
                    continue
                seen.add(tok)
                bare = re.sub(r"^[\w./-]+:(?=[\w.-]+/)", "", tok.strip().rstrip(".,;:)"))
                missing.append((i, m.start(), tok, bare))
        history = self._in_history([t for _, _, _, t in missing])
        where = f"does not exist in {self.tree.head()}" + (" or master" if self.master() else "")
        for i, col, tok, t in missing:
            was, sent = history.get(t), self.text.sentence(i, col)
            if was:
                self.add(WARNING, i + 1, "xref.path", f"`{tok}` {where} (it existed until {was}: a renamed or "
                         "removed file)")
            elif t.startswith("results/"):
                self.add(WARNING, i + 1, "xref.path", f"`{tok}` {where} (a result file, written by a run)")
            elif t.startswith(BUILD_DIRS):
                self.add(WARNING, i + 1, "xref.path", f"`{tok}` {where} (code not built yet: the build follows the "
                         "pin)")
            elif re.search(r"\bscratch\b", sent, re.IGNORECASE):
                self.add(WARNING, i + 1, "xref.path", f"`{tok}` {where} (a scratch file, kept outside the "
                         "repository)")
            elif MADE_LATER.search(sent):
                self.add(WARNING, i + 1, "xref.path", f"`{tok}` {where} (the text may say it is made later)")
            else:
                self.add(ERROR, i + 1, "xref.path", f"`{tok}` {where}, now or in any commit")

    def _in_history(self, paths: list[str]) -> dict[str, str]:
        """{path: the last commit (any branch) that touched it} for the paths ever committed (a bare file name: any
        path ending in it; a path: under any of the resolution prefixes); one `git log` for all of them."""
        if not paths:
            return {}
        specs = sorted({s for t in paths for s in ([f":(glob)**/{t}", t] if "/" not in t
                                                    else [p + t for p in PATH_PREFIXES])})
        r = _git(self.tree.repo, "log", "--all", "--format=@%h", "--name-only", "--", *specs)
        out: dict[str, str] = {}
        commit = ""
        for ln in r.stdout.splitlines() if r.returncode == 0 else []:
            if ln.startswith("@"):
                commit = ln[1:]
                continue
            for t in paths:
                if t not in out and ln and (ln == t or ln.endswith("/" + t)):
                    out[t] = commit
        return out

    def _sha256s(self) -> None:
        body = "\n".join("" if f else line for line, f in zip(self.text.lines, self.text.fenced))
        for m in SHA256_CITE.finditer(body):
            rel, shaped = self._resolve(m.group("path"))
            if not shaped or rel is None:
                continue
            commit = SHA.search(m.group("mid"))
            data = self.tree.read_at(commit.group(1), rel) if commit else self.tree.read(rel)
            if data is None:
                continue
            got, want = sha256_lf(data), m.group("hex")
            line = self.text.line_of(m.start("hex"))
            if "." in want or "…" in want:
                head, tail = re.split(r"\.\.\.|…", want)
                ok = got.startswith(head) and got.endswith(tail)
            else:
                ok = got == want
            if not ok:
                at = f" at {commit.group(1)}" if commit else ""
                self.add(ERROR, line, "xref.sha256", f"`{m.group('path')}`{at} has LF sha256 {got[:16]}..., not the "
                         f"cited {want[:16]}...")

    # ------------------------------------------------------------------------------------------ 3. counts
    def _count_lines(self) -> set[int]:
        out: set[int] = set()
        in_count = False
        for i, line in enumerate(self.text.lines):
            if re.match(r"^#{2,4} ", line) and not self.text.fenced[i]:
                in_count = bool(COUNT_HEADING.match(line))
                continue
            if self.text.fenced[i]:
                continue
            if in_count or "k_cells" in line:
                out.add(i)
        return out

    def check_counts(self) -> None:
        done_units: set[int] = set()
        for i in sorted(self._count_lines()):
            a, unit = self.text.unit(i)
            if a in done_units:
                continue
            done_units.add(a)
            plain = re.sub(r"[*`]", "", unit)
            line_no = a + 1
            checked: list[tuple[int, int]] = []
            for m in NUMERIC_EXPR.finditer(plain):
                expr, want = m.group(1), int(m.group(2).replace(",", ""))
                try:
                    got = eval(re.sub(r"[x×]", "*", expr.replace(",", "")), {"__builtins__": {}}, {})
                except Exception:
                    continue
                checked.append(m.span())
                if got != want:
                    self.add(ERROR, line_no, "count.mismatch", f"{expr.strip()} is {got}, not {want}")
            for s, e, factors, number in self._products(plain):
                if any(cs <= s and e <= ce for cs, ce in checked):
                    continue
                values = [self._factor_value(f) for f in factors]
                shown = " x ".join(f.strip() for f in factors)
                symbolic = [f.strip() for f, v in zip(factors, values) if v is None]
                if number is None:
                    if symbolic:
                        self.add(ERROR, line_no, "count.no-number", f"the product {shown[:120]!r} has no number, and "
                                 f"its factor(s) {symbolic[:3]} are not numbers written here (the template: written as "
                                 "a product and a number)")
                    else:
                        prod = 1
                        for v in values:
                            prod *= v
                        self.add(ERROR, line_no, "count.no-number", f"the product {shown[:120]!r} (= {prod}) is not "
                                 "followed by its number (the template: written as a product and a number)")
                elif symbolic:
                    self.add(WARNING, line_no, "count.symbolic", f"the product {shown[:120]!r} = {number}: factor(s) "
                             f"{symbolic[:3]} are not numbers written here, so the product cannot be checked")
                else:
                    prod = 1
                    for v in values:
                        prod *= v
                    if prod != number:
                        self.add(ERROR, line_no, "count.mismatch", f"the product {shown[:120]!r} is {prod}, not "
                                 f"{number}")
            k = K_CELLS_NUMBER.search(plain)
            if k and not OP.search(plain) and not NUMERIC_EXPR.search(plain):
                self.add(ERROR, line_no, "count.no-product", f"k_cells = {k.group(1)} is written with no product of "
                         "the cells' factors (the template: written as a product and a number)")

    @staticmethod
    def _products(unit: str) -> list[tuple[int, int, list[str], int | None]]:
        """Each product chain `F x F (x F)*` of a unit (factors bounded by , ; : . or a clause start), with the
        number written after it (`= N`, `: N`, `is N`, or a table row's lone number cell), or None."""
        out = []
        ops = list(OP.finditer(unit))
        if not ops:
            return out
        k = 0
        while k < len(ops):
            chain = [ops[k]]
            while k + 1 < len(ops):
                between = unit[chain[-1].end():ops[k + 1].start()]
                if re.search(r"[,;:.](?:\s|$)", Lint._strip_parens(between)):
                    break
                chain.append(ops[k + 1])
                k += 1
            k += 1
            left = Lint._strip_back(unit[:chain[0].start()])
            s = chain[0].start() - len(left)
            factors = [left]
            for a, b in zip(chain, chain[1:]):
                factors.append(unit[a.end():b.start()])
            rest = unit[chain[-1].end():]
            last = Lint._strip_fwd(rest)
            factors.append(last)
            e = chain[-1].end() + len(last)
            if any(re.search(r"[<>≤≥]", f) for f in factors) or \
                    any(len(Lint._strip_parens(f).split()) > 6 for f in factors):
                continue                            # a formula or a sentence, not a count's factors
            after = unit[e:e + 40]
            num = re.match(r"\s*\)?\s*(?:=|:|is|are|gives|makes|totals?)\s*\(?\s*(\d[\d,]*)(?!\d|\.\d)", after)
            number: int | None = int(num.group(1).replace(",", "")) if num else None
            if number is None and unit.lstrip().startswith("|"):
                cells = [c.strip() for c in unit.split("|")]
                lone = [c for c in cells if re.fullmatch(r"\d[\d,]*", c)]
                if len(lone) == 1:
                    number = int(lone[0].replace(",", ""))
            if number is None and unit[:s].rstrip().endswith("(") and unit[e:].lstrip().startswith(")"):
                before = [int(x.replace(",", "")) for x in re.findall(r"(?<![\w.])(\d[\d,]*)(?![\w.])",
                                                                       unit[max(0, s - 80):s])]
                vals = [Lint._factor_value(f) for f in factors]
                if before and None not in vals:
                    prod = 1
                    for v in vals:
                        prod *= v
                    number = prod if prod in before else before[-1]    # "4 evaluations (2 bases x 2 sets)"
                elif before:
                    number = before[-1]
            out.append((s, e, factors, number))
        return out

    @staticmethod
    def _strip_parens(s: str) -> str:
        prev = None
        while prev != s:
            prev, s = s, re.sub(r"\([^()]*\)", "", s)
        return s

    @staticmethod
    def _strip_back(s: str) -> str:
        """The factor before an operator: back to a clause boundary outside parentheses."""
        depth, j = 0, len(s)
        while j > 0:
            c = s[j - 1]
            if c == ")":
                depth += 1
            elif c == "(":
                if depth == 0:
                    break
                depth -= 1
            elif depth == 0 and (c in ",;:|" or (c == "." and (j == len(s) or s[j:j + 1] == " "))):
                break
            j -= 1
        return s[j:]

    @staticmethod
    def _strip_fwd(s: str) -> str:
        depth, j = 0, 0
        while j < len(s):
            c = s[j]
            if c == "(":
                depth += 1
            elif c == ")":
                if depth == 0:
                    break
                depth -= 1
            elif depth == 0 and (c in ",;:|=" or (c == "." and (j + 1 == len(s) or s[j + 1] == " "))):
                break
            elif depth == 0 and s[j:j + 4] in (" per", " eac", " is ", " are"):
                break
            j += 1
        return s[:j]

    @staticmethod
    def _factor_value(f: str) -> int | None:
        f = f.strip()
        m = re.fullmatch(r"\((.*)\)", f, re.DOTALL)
        inner = m.group(1) if m else None
        if inner is not None:
            eq = re.search(r"=\s*(\d[\d,]*)\s*$", inner)
            if eq:
                return int(eq.group(1).replace(",", ""))
            if re.fullmatch(r"\d[\d,]*", inner.strip()):
                return int(inner.strip().replace(",", ""))
            parts = re.split(r"\s(\+|-|less|minus|plus)\s", inner.strip())     # "(16 inventory + 4 Back2Funded)"
            if len(parts) > 1:
                total, sign = 0, 1
                for k, part in enumerate(parts):
                    if k % 2:
                        sign = -1 if part in ("-", "less", "minus") else 1
                        continue
                    lead = re.match(r"(\d[\d,]*)(?!\d|\.\d)", part)
                    if not lead:
                        return None
                    total += sign * int(lead.group(1).replace(",", ""))
                return total
            return None
        lead = re.match(r"(\d[\d,]*)(?!\d|\.\d)", f)
        if lead:
            return int(lead.group(1).replace(",", ""))
        w = re.match(r"([a-z]+)\b", f.lower())
        if w and w.group(1) in SPELLED:
            return SPELLED[w.group(1)]
        return None

    # ------------------------------------------------------------------------------------------ 4. seeds
    def _seed_modules(self, dirs: tuple[str, ...]) -> list[dict]:
        """The modules under `dirs` defining a `SEED_BLOCK`, each read by `guard_constants` (never imported)."""
        if self.tree.rev:
            r = _git(self.tree.repo, "grep", "-l", "SEED_BLOCK", self.tree.rev, "--", *dirs)
            files = [x.split(":", 1)[1] for x in r.stdout.splitlines() if ":" in x]
        else:
            r = _git(self.tree.repo, "grep", "-l", "--untracked", "SEED_BLOCK", "--", *dirs)
            files = [x for x in r.stdout.splitlines() if x]
        out = []
        for rel in sorted(files):
            if not rel.endswith(".py"):
                continue
            src = self.tree.text(rel)
            g = guard_constants(src, rel) if src else None
            if g is not None:
                out.append(g)
        return out

    @staticmethod
    def _twins(a: str, b: str) -> bool:
        """Two names of one declaration: its draft name and its pinned name (the slug after the id)."""
        slug = lambda n: re.sub(r"^(?:DRAFT_)?(?:F|RD|H)-?[0-9A-Z]*?_", "", PurePosixPath(n).name)   # noqa: E731
        return slug(a) == slug(b)

    def _declares(self, rel: str, s: str) -> bool:
        return s in set(SEED_ROW.findall(self.tree.text(rel) or ""))

    def check_seeds(self) -> None:
        own_rows = set(SEED_ROW.findall(self.text.body))
        lits: dict[str, int] = {}
        for i, line in enumerate(self.text.lines):
            for m in SEED_LIT.finditer(line):
                lits.setdefault(m.group(1), i)
        if not lits and not own_rows:
            return
        guards = self._seed_modules(GUARD_DIRS)
        owners = self._seed_modules(OWNER_DIRS)
        owned = set().union(*(g["block"] for g in owners)) if owners else set()
        owner = {s: [g for g in guards if int(s) in g["block"]] for s in set(lits) | own_rows}
        stage2 = self._in_vendor(set(lits) - own_rows - {s for s, g in owner.items() if g} - {str(x) for x in owned})
        others = [n for n in sorted(self.tree.names) if re.fullmatch(r"prereg/[^/]+\.md", n)
                  and not n.startswith("prereg/TEMPLATE_") and n != self.rel and not self._twins(n, self.rel)]
        reported_blocks: set[int] = set()
        for s, i in sorted(lits.items(), key=lambda x: x[1]):
            gs = owner[s]
            if gs:
                if any(self.rel in g["allowed"] for g in gs):
                    continue
                if s in own_rows:
                    twice = [n for n in others if self._declares(n, s)]
                    if twice:
                        self.add(ERROR, i + 1, "seed.outside-use", f"seed {s} is declared in this file's seed table "
                                 f"and in {twice[0]}'s: one block, one declaration")
                    continue                        # this file declares the block its guard watches
                self.add(ERROR, i + 1, "seed.outside-use", f"seed {s} belongs to the block guarded by "
                         f"{', '.join(g['path'] for g in gs)}, and {self.rel} is not one of its declared uses")
            elif int(s) in owned:
                continue                            # an inherited seed, drawn by the code that owns its block
            elif s in own_rows:
                key = int(s) // 10
                if key not in reported_blocks:
                    reported_blocks.add(key)
                    self.add(WARNING, i + 1, "seed.unguarded", f"seed {s}: no seed guard (a module defining "
                             "SEED_BLOCK) holds this block (the template: a test of the draft refuses its block in "
                             "any other declaration)")
            elif s not in stage2:
                self.add(WARNING, i + 1, "seed.undeclared", f"{s} is seed-shaped but is in no seed table here, no "
                         "seed guard's block and not Stage 2's")
        self._cited_files_hold_seeds(guards, own_rows)

    def _in_vendor(self, seeds: set[str]) -> set[str]:
        if not seeds:
            return set()
        args = ["grep", "-h", "-o", "-w", "-F"] + [x for s in sorted(seeds) for x in ("-e", s)]
        args += [self.tree.rev] if self.tree.rev else []
        r = _git(self.tree.repo, *args, "--", "vendor/stage2")
        return {ln.rsplit(":", 1)[-1].strip() for ln in r.stdout.splitlines()} & seeds

    def _cited_files_hold_seeds(self, guards: list[dict], own_rows: set[str]) -> None:
        if not own_rows:
            return
        strict = [g for g in guards if g["strict"] and any(int(s) in g["block"] for s in own_rows)]
        allowed = set().union(*(g["allowed"] for g in strict)) if strict else set()
        pat = re.compile(r"(?<![\w.-])(" + "|".join(sorted(own_rows)) + r")(?![\w-]|\.\d)")
        seen = set()
        for i, line in self.own_lines():
            for m in BACKTICK.finditer(line):
                rel, _ = self._resolve(m.group(1))
                if rel is None or rel in seen or rel == self.rel or not rel.endswith(TEXT_EXT) \
                        or rel.startswith(("vendor/",) + SEED_RECORD) or self._twins(rel, self.rel):
                    continue
                seen.add(rel)
                t = self.tree.text(rel)
                hit = pat.search(t) if t else None
                if not hit:
                    continue
                if strict and rel not in allowed:
                    self.add(ERROR, i + 1, "seed.cited-file", f"the cited `{rel}` holds seed {hit.group(1)} of this "
                             f"declaration's block, outside {strict[0]['path']}'s DECLARED_USES")
                elif not strict and re.fullmatch(r"prereg/[^/]+\.md", rel):
                    self.add(ERROR, i + 1, "seed.cited-file", f"the cited declaration `{rel}` holds seed "
                             f"{hit.group(1)} of this declaration's block (a block is found nowhere else)")

    # ------------------------------------------------------------------------------------------ 5. tokens
    def check_tokens(self) -> None:
        for i, line in self.own_lines():
            hits: list[tuple[int, str]] = []
            for m in IT.TOKEN_LIKE.finditer(line):
                hits.append((m.start(), "identity"))
            for m in RD.HELDOUT_TOKEN_LIKE.finditer(line):
                hits.append((m.start(), "heldout"))
            for m in CLOSED_LIKE.finditer(line):
                hits.append((m.start(), "closed"))
            for m in GO_LIKE.finditer(line):
                hits.append((m.start(), "go"))
            for start, kind in sorted(hits):
                self._token(i, line, start, kind)

    def _token(self, i: int, line: str, start: int, kind: str) -> None:
        is_row = bool(re.match(r"^\| (?:E-\d+|E-NNN) \|", line))
        third = re.match(r"\|[^|]*\|[^|]*\| ", line) if is_row else None
        at_position = bool(third and start == third.end())
        quoted = line.rfind("`", 0, start) > line.rfind("`", 0, start - 1 if start else 0) - 1 and \
            line.count("`", 0, start) % 2 == 1
        if quoted:
            end = line.find("`", start)
            raw = line[start:end if end > 0 else len(line)]
        else:
            end = line.find("|", start)
            raw = line[start:end if end > 0 else len(line)].rstrip()
        has_placeholder = bool(re.search(r"<[^<>]+>|\bF-(?:NN|XX|HT)\b|\bQ-nn\b|\bE-NNN\b", raw))
        if kind == "identity" and IT.PLACEHOLDER.match(line, start) and not at_position:
            return                                  # `identity-holds: <id>`, the identity-token test's own placeholder
        cand = raw
        if kind == "identity":                      # a commit sha there, 7 to 40 hexadecimal characters
            cand = re.sub(r"<[^<>]*sha[^<>]*>", "0" * 7, cand)
        for rx, sub in PLACEHOLDER_SUBS:
            cand = rx.sub(sub, cand)
        if " -- " not in cand:
            cand = cand.rstrip(" .,;") + " -- text"
        row = "| E-999 | 2026-01-01 | " + cand
        stem = cand.split(":", 1)[0].strip().lower()
        ok = self._grammar(kind, stem, row)
        if not ok:
            self.add(ERROR, i + 1, "token.grammar", f"{raw[:80]!r} is not in the grammar the reader and the "
                     f"identity-token test accept ({self._grammar_hint(kind, stem)})")
            return
        if has_placeholder:
            return
        if not at_position:
            self.add(ERROR, i + 1, "token.position", f"{raw[:60]!r} is a real token outside a decision row's token "
                     "position (only the first text of a row's third cell is a token; write a placeholder form here)")

    @staticmethod
    def _grammar(kind: str, stem: str, row: str) -> bool:
        if kind == "identity":
            return bool(IT.TOKEN.match(row))
        if kind == "go":
            return bool(GO.match(row))
        if kind == "closed":
            return bool(CLOSED.match(row))
        for k, rx in RD.HELDOUT_TOKENS.items():
            if stem == f"heldout-{k}" and rx.match(row):
                return True
        return False

    @staticmethod
    def _grammar_hint(kind: str, stem: str) -> str:
        return {"identity": "identity-holds: <id> @ <sha> -- <text>",
                "go": "go: F-NN @ <its LF sha256> -- <text>",
                "closed": "heldout-closed: F-NN @ <its LF sha256> -- <cause> -- <text>"}.get(
            kind, "heldout-finalists: F-NN @ <sha256> list <sha256>; heldout-window: NQ <first> to <last>; "
                  "heldout-verdict: NQ F-NN @ <sha256>; heldout-read: P-14,P-16 by scripts/<x>.py; heldout-void: "
                  "E-NNN; each followed by ' -- <text>'")

    # ------------------------------------------------------------------------------------------ 6. dates
    def check_dates(self) -> None:
        judged_line = bool(RD.declared_purposes(self.text.body))
        program_start = self._program_start()
        for i, raw in self.own_lines():
            line = re.sub(r"\"[^\"\n]*\"|\u201c[^\u201d\n]*\u201d", lambda q: " " * len(q.group(0)), raw)
            ranges = {m.start(2): m.group(1) for m in RANGE.finditer(line)}
            for m in DATE.finditer(line):
                try:
                    d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                except ValueError:
                    continue
                sent = self.text.sentence(i, m.start())
                data_date = d < program_start or (m.start() in ranges and ranges[m.start()] < str(program_start))
                if d >= CONFIRMATION and data_date:
                    if not DATA_WORD.search(sent):
                        continue                    # a calendar date (a rule's verification, a firm's terms)
                    if NEVER.search(sent) or NEGATION.search(sent) or RESERVE.search(sent) \
                            or (CONFIRMATION_DECL.search(sent) and CONFIRMATION_TERMS.search(sent)) \
                            or CONFIRMATION_DECL.search(self._heading(i)):
                        continue
                    self.add(ERROR, i + 1, "date.confirmation", f"{m.group(0)} is in the confirmation window (NQ from "
                             f"2026-07-17), named here not as a refusal: {sent.strip()[:100]!r}")
                elif HELD_OUT[0] <= d <= HELD_OUT[1] and not judged_line:
                    rest = NEVER.sub(" ", sent)
                    if NEVER.search(sent) and not READ_WORD.search(rest):
                        continue
                    if NEVER.search(sent) and re.search(r"\bunless\b|\brefus\w*", sent, re.IGNORECASE):
                        continue
                    self.add(ERROR, i + 1, "date.heldout", f"{m.group(0)} is in the held-out years, named outside a "
                             "never-read statement, and this file carries no `Judged-block reads:` line: "
                             f"{sent.strip()[:100]!r}")

    def _heading(self, i: int) -> str:
        """The heading of the section holding line `i`."""
        for j in range(i, -1, -1):
            if self.text.lines[j].startswith("#") and not self.text.fenced[j]:
                return self.text.lines[j]
        return ""

    def _program_start(self) -> date:
        m = re.search(r"^\| E-\d+ \| (\d{4})-(\d\d)-(\d\d) \|", self.decisions, re.MULTILINE)
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else date(2026, 11, 1)

    # ------------------------------------------------------------------------------------------ 7. typed figures
    def check_figures(self) -> None:
        known: set[str] = set()
        for rel in ("CHARTER.md", "docs/MEASURES.md"):
            t = self.tree.text(rel) or ""
            known |= set(DECIMAL.findall(t)) | {p.replace(" ", "") for p in PERCENT.findall(t)}
        for t in self.templates.values():
            known |= set(DECIMAL.findall(t.body)) | set(PERCENT.findall(t.body))
        heads = {n for n, _, _, _ in self.text.sections()}
        for i, line in self.own_lines():
            if line.startswith("#"):
                continue
            secnums = {m.group(1) for m in SECTION_NUMBER.finditer(line)}
            for rx, what in ((DECIMAL, "decimal"), (PERCENT, "percentage")):
                for m in rx.finditer(line):
                    v = m.group(1)
                    if v in known or v in secnums or v.split(".")[0] in heads and what == "decimal" and len(v) <= 4:
                        continue
                    if what == "decimal" and len(v.replace(".", "").lstrip("0").rstrip("0") or "0") < 3:
                        continue
                    if what == "decimal" and re.match(r"\s*\(|'s\b", line[m.end():m.end() + 2]):
                        continue                    # "2.2 (a)", "10.2's window rule": a section or clause number
                    if what == "percentage" and re.match(r"\s*(?:rules?|consistency|cap|share)\b",
                                                         line[m.end():m.end() + 14]):
                        continue                    # "the 45 % rule": a rule's value, named as one
                    if what == "decimal" and (UNIT_AFTER.match(line[m.end():m.end() + 9])
                                              or line[max(0, m.start() - 1):m.start()] == "$"):
                        continue                    # contract arithmetic or a price: "37.5 points", "$115.50"
                    if line.lstrip().startswith("|"):
                        if FINDING_ROW.match(line.lstrip()):
                            continue                # a row answering a review's finding cites its measurement
                        sent = line
                    else:
                        sent = self.text.sentence(i, m.start())
                    if FIGURE_LABEL.search(sent):
                        continue
                    self.add(WARNING, i + 1, "figure.typed", f"a result-shaped {what} {m.group(0).strip()!r} on a "
                             "line labelled as no rule value, seed, declared parameter, known answer or cited "
                             "measurement (a result is cited by its file, never typed)")


# =================================================================================================== seed guards

def guard_constants(src: str, rel: str) -> dict | None:
    """A seed guard's own constants -- `SEED_BLOCK` (a tuple of ints) and the files it allows (`DECLARED_USES`,
    `DERIVED_USES`, the guard itself, and its path constants) -- evaluated from its module-level assignments, in
    order, with no builtins but tuple, range, int, str, len, set and frozenset; the module is never imported."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    ns: dict = {"__builtins__": {"tuple": tuple, "range": range, "int": int, "str": str, "len": len, "set": set,
                                 "frozenset": frozenset, "list": list},
                "ROOT": PurePosixPath("."), "THIS": rel, "Path": PurePosixPath, "PurePosixPath": PurePosixPath}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            name, value = node.target.id, node.value
        else:
            continue
        if name in ("ROOT", "THIS") or any(isinstance(n, ast.Attribute) and n.attr.startswith("_")
                                            or isinstance(n, ast.Name) and n.id.startswith("__")
                                            for n in ast.walk(value)):
            continue
        try:
            ns[name] = eval(compile(ast.Expression(value), rel, "eval"), ns)      # noqa: S307 (restricted, no import)
        except Exception:
            continue
    block = ns.get("SEED_BLOCK")
    if not (isinstance(block, tuple) and block and all(isinstance(x, int) for x in block)):
        return None
    allowed = {rel}
    homes = []
    for k, v in ns.items():
        if k.startswith("__"):
            continue
        vals = v if isinstance(v, (tuple, list, set, frozenset)) else (v,)
        for x in vals:
            if isinstance(x, PurePosixPath):
                x = x.as_posix()
            if not isinstance(x, str) or not re.fullmatch(r"[\w./-]+\.(?:md|py|json|yaml|csv|txt)", x):
                continue
            if "/" not in x and re.match(r"(?:DRAFT_|F-|RD-|H\d)", x):
                x = f"prereg/{x}"
            allowed.add(x)
            if x.startswith(("prereg/", "docs/")):
                homes.append(x)
    #: a guard with an explicit DECLARED_USES scans the whole tree (its uses are the only files allowed); one without
    #: one refuses its block in the other declarations only
    return {"path": rel, "block": set(block), "allowed": allowed, "homes": homes, "strict": "DECLARED_USES" in ns}


# =================================================================================================== the command

def lint(decl: Path, repo: Path = ROOT, rev: str | None = None, rel: str | None = None,
         templates: Iterable[Path] = (), decisions: str | None = None, pin: bool | None = None) -> list[Problem]:
    return Lint(decl, Tree(repo, rev), rel=rel, templates=templates, decisions=decisions, pin=pin).run()


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("path", type=Path, help="the declaration to lint")
    ap.add_argument("--repo", type=Path, default=ROOT, help="the repository its citations resolve in (default: this)")
    ap.add_argument("--rev", help="resolve cited files and templates in this commit's tree, and commits from it")
    ap.add_argument("--as", dest="rel", help="the declaration's repository path, when the file lives elsewhere")
    ap.add_argument("--template", type=Path, action="append", default=[], help="a template file to add or replace")
    ap.add_argument("--decisions", type=Path, help="the decision log to read rows from (default: master's)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--pin", dest="pin", action="store_true", default=None, help="apply the pin-time form checks")
    g.add_argument("--draft", dest="pin", action="store_false", help="skip the pin-time form checks")
    a = ap.parse_args(argv)
    try:
        dec = a.decisions.read_text(encoding="utf-8").replace("\r\n", "\n") if a.decisions else None
        found = lint(a.path, a.repo.resolve(), a.rev, a.rel, a.template, dec, a.pin)
    except (OSError, RuntimeError) as e:
        print(f"decl_lint: cannot run: {e}", file=sys.stderr)
        return 2
    errors = [p for p in found if p.severity == ERROR]
    warnings = [p for p in found if p.severity == WARNING]
    n = 0
    for title, group in (("errors", errors), ("warnings (do not fail the exit code)", warnings)):
        if group:
            print(f"{title}:")
            for p in group:
                n += 1
                print(f"{n:3d}. {p.render()}")
    print(f"decl_lint: {len(errors)} error(s), {len(warnings)} warning(s) in {a.path.as_posix()}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
