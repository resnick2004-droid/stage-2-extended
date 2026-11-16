"""The identity-holds tokens of `DECISIONS.md` (E-098's rule in E-104's positional form; Q-110): which rows record an
identity holding and at which commit, whether a runner's wait is met, and the breaches. **The one parser every runner
imports** (E-104: RD-01's, RD-02's, F-03's): `parse` (the tokens), `held` (a wait; `held_report` adds why each row
did not qualify), `problems` (the breaches), `occurrences` (every token-like string, classed).

**The rule.** A row recording that an identity holds carries exactly one token, the first text of its third cell:

    | E-NNN | YYYY-MM-DD | identity-holds: <id> @ <sha> -- <text> | <sources> |

unquoted; `<id>` names the identity, `<sha>` the commit it held at. That shape anywhere else -- later in the cell, in
another cell, in another line, backticked or not -- is never a token; a row describing tokens writes a placeholder.
The same id may be held again at a newer commit in a new row (an identity is re-held after its code changes).

**The grammar** (`TOKEN`, matched at a line's start; every part exact):

* the row's start: a bar, one space, `E-` and digits, one space, a bar, one space, a date `YYYY-MM-DD`, one space, a
  bar, one space;
* the stem `identity-holds`, a colon, one space;
* the id: a queue id -- `Q-`, digits, at most one lowercase letter (`Q-80`, `Q-04`, `Q-104d`) -- or a runner's label
  -- a lowercase letter, then lowercase letters, digits and underscores (`pp_identity`, `t10w2`); the id ends where
  ` @ ` begins, so `Q-8` is never read in `Q-80`, `Q-800` or `Q-80x`;
* ` @ `, then the sha: 7 to 40 lowercase hexadecimal characters, ending where ` -- ` begins;
* ` -- `, then the row's text, whose first character is neither a space nor a bar.

The placeholders, never ids: `<id>` (E-104's) and `Q-nn` (E-098's and E-099's).

**A token-like string** is what a hand meaning a token types: `identity` and `holds` (or `hold`, `held`) joined by a
hyphen, a hyphen-like character, an underscore or nothing, in any case, then optional spaces and a colon (or `=`), or
spaces and a queue id. Not token-like: `identity holds: Q-80` -- a space for the hyphen, prose (the identity scripts
print `identity HOLDS: ...` and rows quote them) -- and a mention without the colon (`the identity-holds token`).

**The token position** of a row (a line `extended.reader.ROW` matches at its start, as the runners read rows): the
third cell's first text, after any spaces, backticks or emphasis marks (`*`, `_`, `~`).

**`problems`, the breaches.** Mechanical: a floor under the rule, not a proof of it -- they cannot read whether a row
truly records an identity holding; the lead's discipline remains the rule. Each message begins with its letter.

* (a) two rows carrying tokens with the same id and the same sha (a sha and a longer form of it name one commit);
* (b) a token whose row, outside the token, has none of the words `holds`, `HOLDS`, `held` -- whole words, neither
  letter, digit, underscore nor hyphen on either side, so `withheld`, `upheld`, `held-out`, `thresholds`, `Holds` and
  the stem's own `-holds` do not count;
* (c) a malformed token: a token-like string at the token position that is not exactly the grammar -- the row's start
  not exact, anything but one space before it (backticks and emphasis included), the stem's spelling, the colon's
  spacing, a bad id (a placeholder there included), no ` @ `, a bad sha, no ` -- `, no text, a backtick in it;
* (d) a token-like string anywhere else -- a later place in the third cell, another cell, a line that is no row --
  unless it is exactly a placeholder (`identity-holds: ` and then `<id>`, or `Q-nn` not followed by a letter, digit,
  underscore or hyphen). Harmless to a runner (`parse` never reads it), but it is the confusion the rule exists to
  prevent; the lead rewrites such wording in the next row.

**`held(text, ident, repo, head, covered)`**: of the rows carrying a token for exactly `ident`, the newest (the highest
E-number; file order breaks a tie) such that (1) the row has no breach (b); (2) its sha resolves in `repo` to a
commit that is `head` or an ancestor of it (`git merge-base --is-ancestor`); (3) none of the `covered` paths differs
between that commit and `head` (`git diff --quiet <sha> <head> -- <covered>`, literal pathspecs). None if no row
qualifies. Commits only: a working tree's uncommitted edits are not seen (a runner runs from a clean checkout).
Refused (`ValueError`): an `ident` outside the grammar, no covered path, a path that is absolute or not in `head`, a
`head` that is not a commit. `covered` is a list of repository-relative paths (`\\` read as `/`), not patterns; a
folder covers everything under it.

Pure Python and git; nothing here reads data or imports the engine.
"""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import NamedTuple, Sequence

STEM = "identity-holds"
QUEUE_ID = r"Q-\d+[a-z]?"
LABEL = r"[a-z][a-z0-9_]*"
#: an id, whole: a queue id or a runner's label
ID = re.compile(rf"{QUEUE_ID}|{LABEL}")
#: the rule's own examples, never ids
PLACEHOLDERS = ("<id>", "Q-nn")
#: a decision row, at a line's start, as `extended.reader.ROW` and the runners read rows
ROW = re.compile(r"\|\s*(E-\d+)\s*\|")
#: the row's exact start, up to the token
ROW_START = re.compile(r"\| E-\d+ \| \d{4}-\d{2}-\d{2} \| ")
#: a row's first two cells (loosely): their end is the third cell's start
THIRD_CELL = re.compile(r"\|\s*E-\d+\s*\|[^|]*\|")
#: what may stand before the token position's first text: spaces, backticks, emphasis marks
MARKS = re.compile(r"[\s`*_~]*")
#: the token, whole, at a line's start
TOKEN = re.compile(rf"\| (?P<row>E-\d+) \| \d{{4}}-\d{{2}}-\d{{2}} \| {STEM}: (?P<ident>{QUEUE_ID}|{LABEL}) @ "
                   r"(?P<sha>[0-9a-f]{7,40}) -- (?=[^\s|])")
#: a character class's body: the hyphen (escaped), the underscore, the soft hyphen, the hyphens and dashes, minus
_JOINERS = "\\-_\u00ad\u2010-\u2015\u2212"
#: a token-like string (its stem in group `stem`)
TOKEN_LIKE = re.compile(rf"(?P<stem>identity[{_JOINERS}]?(?:holds?|held))(?:\s*[:=\uff1a]|\s+(?=q-\d))",
                        re.IGNORECASE)
#: a placeholder, exactly
PLACEHOLDER = re.compile(rf"{STEM}: (?:<id>|Q-nn(?![\w-]))")
#: the words a token's row must say, whole
HOLDS_WORD = re.compile(rf"(?<![\w{_JOINERS}])(?:holds|HOLDS|held)(?![\w{_JOINERS}])")
_SHA = re.compile(r"[0-9a-f]{7,40}")
_PART = re.compile(r"[^\s|]*")
_AT = re.compile(r"\s*(?:@\s*)?")
#: git's variables that would point a call at another repository or index than `repo`
_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE")


class Token(NamedTuple):
    """A row's token: the row's id, the identity's id, the sha as written."""
    row: str
    ident: str
    sha: str


@dataclass(frozen=True)
class Occurrence:
    """A token-like string: where (1-based line and column, the row's id or None), what (`token`, `malformed`,
    `placeholder`, `elsewhere`), its text from the stem (`ascii`), and why it is malformed (`malformed` only)."""
    line: int
    row: str | None
    column: int
    kind: str
    snippet: str
    reasons: tuple[str, ...] = ()


def _position(line: str) -> tuple[int, int] | None:
    """(the third cell's start, its first text after spaces and marks) of a row; None for a line that is no row."""
    if not ROW.match(line):
        return None
    m = THIRD_CELL.match(line)
    if not m:
        return None
    return m.end(), MARKS.match(line, m.end()).end()


def _snippet(line: str, start: int) -> str:
    end = line.find("|", start)
    return ascii(line[start:(end if end >= 0 else len(line))][:72].rstrip())


def _malformed(line: str, p0: int, m: re.Match) -> tuple[str, ...]:
    """Why the token-like string `m` at a row's token position (its third cell starting at `p0`) is not a token."""
    why: list[str] = []
    cell_end = line.find("|", p0)
    cell_end = len(line) if cell_end < 0 else cell_end
    if not ROW_START.fullmatch(line[:p0] + " "):
        why.append("the row does not begin exactly '| E-NNN | YYYY-MM-DD |' (one space each side of each bar)")
    if line[p0:m.start()] != " ":
        why.append(f"{ascii(line[p0:m.start()])} before the token, where one space belongs (it is unquoted, first)")
    if m.group("stem") != STEM:
        why.append(f"the stem is written {ascii(m.group('stem'))}, not {STEM!r}")
    q = m.end("stem")
    if not (line.startswith(": ", q) and not line[q + 2:q + 3].isspace()):
        why.append("not exactly a colon and one space after the stem")
    j = re.compile(r"\s*[:=\uff1a]?\s*").match(line, q).end()
    ident = _PART.match(line, j).group()
    k = j + len(ident)
    if ident in PLACEHOLDERS:
        why.append(f"the placeholder {ident} where a real id belongs")
    elif not ID.fullmatch(ident):
        why.append(f"the id {ascii(ident)} is neither a queue id (Q-80, Q-104d) nor a lowercase label (pp_identity)")
    end = cell_end
    at = _AT.match(line, k)
    if "@" in line[k:at.end()] and not line.startswith(" @ ", k):
        why.append("not exactly ' @ ' after the id")
    if "@" in line[k:at.end()]:
        sha = _PART.match(line, at.end()).group()
        s = at.end() + len(sha)
        if not _SHA.fullmatch(sha):
            why.append(f"the sha {ascii(sha)} is not 7 to 40 lowercase hexadecimal characters")
        if not line.startswith(" -- ", s):
            why.append("not exactly ' -- ' after the sha")
        else:
            end = s + 4
            if line[end:end + 1] in ("", "|") or line[end:end + 1].isspace():
                why.append("no text after ' -- ' (its first character neither a space nor a bar)")
    else:
        why.append("no ' @ ' and sha after the id")
    if "`" in line[p0:end]:
        why.append("a backtick in or around the token (it is written unquoted)")
    return tuple(why) or ("not exactly the form 'identity-holds: <id> @ <sha> -- <text>'",)


def occurrences(text: str) -> list[Occurrence]:
    """Every token-like string of `text`, in order, each classed: `token` (at a row's token position, exactly the
    grammar), `malformed` (at the position, not exactly it: breach (c)), `placeholder` (elsewhere, exactly a
    placeholder) or `elsewhere` (anything else: breach (d))."""
    out: list[Occurrence] = []
    for n, line in enumerate(text.splitlines(), start=1):
        r = ROW.match(line)
        rid = r.group(1) if r else None
        pos = _position(line)
        for m in TOKEN_LIKE.finditer(line):
            snip = _snippet(line, m.start())
            if pos is not None and m.start() == pos[1]:
                if TOKEN.match(line):
                    out.append(Occurrence(n, rid, m.start() + 1, "token", snip))
                else:
                    out.append(Occurrence(n, rid, m.start() + 1, "malformed", snip, _malformed(line, pos[0], m)))
            elif PLACEHOLDER.match(line, m.start()):
                out.append(Occurrence(n, rid, m.start() + 1, "placeholder", snip))
            else:
                out.append(Occurrence(n, rid, m.start() + 1, "elsewhere", snip))
    return out


def _tokens(text: str) -> list[tuple[int, Token, str]]:
    """(line number, token, the row's text after the token) of every row carrying one, in order."""
    out = []
    for n, line in enumerate(text.splitlines(), start=1):
        m = TOKEN.match(line)
        if m:
            out.append((n, Token(m["row"], m["ident"], m["sha"]), line[m.end():]))
    return out


def parse(text: str) -> list[Token]:
    """Every row's token, in file order: positional only (`TOKEN` at a line's start), nothing else ever read."""
    return [t for _, t, _ in _tokens(text)]


def says_held(rest: str) -> bool:
    """Whether a token's row text (outside the token) says `holds`, `HOLDS` or `held` as a whole word."""
    return HOLDS_WORD.search(rest) is not None


def problems(text: str) -> list[str]:
    """The breaches (a) to (d) of the module's docstring, in line order, each message beginning with its letter; [] is
    clean. No message is itself a token."""
    found: list[tuple[int, int, str]] = []
    toks = _tokens(text)
    for i, (n, t, rest) in enumerate(toks):
        for _, u, _ in toks[:i]:
            if u.ident == t.ident and (u.sha.startswith(t.sha) or t.sha.startswith(u.sha)):
                found.append((n, 0, f"(a) {t.row} repeats {u.row}'s token for {t.ident} at {t.sha}: one row records "
                                    "an identity holding at one commit"))
                break
        if not says_held(rest):
            found.append((n, 1, f"(b) {t.row} carries the token for {t.ident} at {t.sha} but says neither holds, "
                                "HOLDS nor held (whole words, outside the token)"))
    for o in occurrences(text):
        where = o.row if o.row else f"line {o.line} (not a decision row)"
        if o.kind == "malformed":
            found.append((o.line, 2, f"(c) {where}: a malformed token at column {o.column}, {o.snippet}: "
                                     + "; ".join(o.reasons)))
        elif o.kind == "elsewhere":
            found.append((o.line, 3, f"(d) {where}: an identity-holds string at column {o.column}, {o.snippet}, "
                                     "outside the token position and not a placeholder (<id>, Q-nn): never a token; "
                                     "reword it in the next row"))
    return [msg for _, _, msg in sorted(found, key=lambda x: (x[0], x[1]))]


# --- held ------------------------------------------------------------------------------------------------------------

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in _GIT_ENV}
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, env=env, timeout=300)


def _commit(repo: Path, rev: str) -> str | None:
    """The full hash of the commit `rev` names in `repo`, or None."""
    if not rev or rev.startswith("-"):
        return None
    r = _git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    full = r.stdout.strip()
    return full if r.returncode == 0 and full else None


def _paths(covered: Sequence[str | os.PathLike]) -> list[str]:
    if isinstance(covered, (str, bytes, os.PathLike)):
        raise TypeError("covered is a list of paths, not one path")
    out = []
    for c in covered:
        p = os.fspath(c)
        if os.path.isabs(p) or PureWindowsPath(p).drive or p.startswith(("/", "\\")):
            raise ValueError(f"covered path {p!r}: repository-relative paths only")
        p = p.replace("\\", "/").rstrip("/")
        if not p or p.startswith("-"):
            raise ValueError(f"covered path {os.fspath(c)!r} is not a path")
        out.append(p)
    if not out:
        raise ValueError("an identity covers the code it held on: no covered path given")
    return out


def held_report(text: str, ident: str, repo: Path | str, head: str, covered: Sequence[str | os.PathLike]
                ) -> tuple[Token | None, list[str]]:
    """`held`'s answer and why each newer row carrying `ident`'s token did not qualify (or that none carries one)."""
    if not isinstance(ident, str) or not ID.fullmatch(ident):
        raise ValueError(f"{ident!r} is neither a queue id nor a lowercase label")
    paths = _paths(covered)
    repo = Path(repo)
    head_full = _commit(repo, head)
    if head_full is None:
        raise ValueError(f"head {head!r} is not a commit of {repo}")
    for p in paths:
        if _git(repo, "cat-file", "-e", f"{head_full}:{p}").returncode != 0:
            raise ValueError(f"covered path {p!r} is not in {head} ({head_full[:12]})")
    cands = [(n, t, rest) for n, t, rest in _tokens(text) if t.ident == ident]
    cands.sort(key=lambda x: (int(x[1].row[2:]), x[0]), reverse=True)
    why: list[str] = []
    for _, t, rest in cands:
        if not says_held(rest):
            why.append(f"{t.row}: its row says neither holds, HOLDS nor held (breach (b))")
            continue
        full = _commit(repo, t.sha)
        if full is None:
            why.append(f"{t.row}: {t.sha} is not a commit of {repo}")
            continue
        anc = _git(repo, "merge-base", "--is-ancestor", full, head_full)
        if anc.returncode == 1:
            why.append(f"{t.row}: {t.sha} is neither {head} nor an ancestor of it")
            continue
        if anc.returncode != 0:
            raise RuntimeError(f"git merge-base --is-ancestor {full[:12]} {head_full[:12]}: {anc.stderr.strip()[:300]}")
        d = _git(repo, "--literal-pathspecs", "diff", "--quiet", full, head_full, "--", *paths)
        if d.returncode == 1:
            names = _git(repo, "--literal-pathspecs", "diff", "--name-only", full, head_full, "--", *paths)
            changed = [x for x in names.stdout.splitlines() if x.strip()]
            why.append(f"{t.row}: {len(changed)} covered file(s) changed since {t.sha}: {', '.join(changed[:5])}")
            continue
        if d.returncode != 0:
            raise RuntimeError(f"git diff {full[:12]} {head_full[:12]}: {d.stderr.strip()[:300]}")
        return t, why
    if not cands:
        why.append(f"no row carries a token for {ident}")
    return None, why


def held(text: str, ident: str, repo: Path | str, head: str, covered: Sequence[str | os.PathLike]) -> Token | None:
    """The newest row recording `ident` held at `head`'s code for the `covered` paths, or None (the module's
    docstring: the three conditions, and what is refused)."""
    return held_report(text, ident, repo, head, covered)[0]


__all__ = ["Token", "Occurrence", "STEM", "ID", "PLACEHOLDERS", "TOKEN", "TOKEN_LIKE", "parse", "occurrences",
           "says_held", "problems", "held", "held_report"]
