"""The design search's go token and the membership event it fixes (G-1, G-2; E-257, E-259).

A design search's go row (`prereg/TEMPLATE_design_search.md`, section 14 step 4) carries, as the first text of the
row's third cell, the token

    | E-NNN | YYYY-MM-DD | go: F-NN @ <the declaration's LF sha256> -- <text> |

The token counts only when all of these hold (G-2):

* it sits **outside any fenced code block** (CommonMark's rule, as `extended/reader.py` reads fences);
* it is in the **exact form** above -- the row's start, `go: `, the F-number, ` @ `, 64 lower-case hex digits, then
  ` -- ` and text whose first character is neither a space nor a bar;
* its sha256 is **its declaration's pinned sha256** (the sha of the declaration's first hash row,
  `` `prereg/F-NN_<slug>.md` sha256 `<64 hex>` ``);
* its row comes **strictly after that hash row** in `DECISIONS.md` (by position, never by E-number).

A row whose third cell begins go-like (after spaces, backticks and emphasis marks, `go:` or `go=` in any case) but is
not a counted token, a go token inside a fence, a token at another sha, a token before its own hash row, and a fence
never closed are **hygiene problems** (`go_problems`): while any stands, nothing here answers (`GoRefused`), as the
reader refuses every judged read while its own log hygiene fails. A problem row is cleared only by a later row
`heldout-void: E-NNN -- <reason>` naming it (the recovery Q-194e gives); a void naming a counted go token, a pin row,
or a held-out finalists' or verdict row is itself a problem.

**The membership event** (H-1'; E-257) is the first counted go token of a declaration in scope -- an NQ design search
of Topstep, My Funded Futures or Lucid, by the declaration's **declared market field** (`- **The market:** NQ`) and
its firm line (`- **The firm and account:** <firm>, ...`), never by searching its text (`declared_scope`). A member is
the one in-scope declaration of its firm whose hash row comes strictly before the event's row; a second in-scope hash
row for a firm before the event is refused (R-1).

`go_row_present(decisions, decl, sha)` is the check the survey runner makes before it starts (section 14 step 4,
"the go row present"): the log clean and a counted go token for that declaration at that sha.

Text only: this module reads `DECISIONS.md` and `prereg/` and nothing else."""
from __future__ import annotations

import re
from pathlib import Path

__all__ = ["GO_TOKEN", "GoRefused", "fences", "go_problems", "go_tokens", "go_row_present", "membership",
           "declared_scope", "FIRM_NAMES"]

#: the go token, exactly the first text of a decision row's third cell (the reader's positional form and tail)
GO_TOKEN = re.compile(r"\| (?P<row>E-\d+) \| (?P<date>\d{4}-\d{2}-\d{2}) \| go: (?P<decl>F-\d+) @ "
                      r"(?P<sha>[0-9a-f]{64}) -- (?=[^\s|])")
#: a go-like start of a third cell, after spaces, backticks and emphasis marks
_GO_LIKE = re.compile(r"go\s*[:=]", re.IGNORECASE)
_ROW = re.compile(r"\| (?P<row>E-\d+) \|")
_THIRD_CELL = re.compile(r"\|\s*E-\d+\s*\|[^|]*\|")
_MARKS = re.compile(r"[\s`*_~]*")
_PIN = re.compile(r"`prereg/(?P<decl>F-\d+)_[^`]*\.md` sha256 `(?P<sha>[0-9a-f]{64})`")
_VOID = re.compile(r"\| (?P<row>E-\d+) \| \d{4}-\d{2}-\d{2} \| heldout-void: (?P<target>E-\d+) -- (?=[^\s|])")
_PROTECTED = re.compile(r"\| E-\d+ \| \d{4}-\d{2}-\d{2} \| heldout-(?:finalists|verdict): ")
_FENCE_OPEN = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")

#: the three firms of the line, by the names a firm line may begin with
FIRM_NAMES = {"Topstep": "Topstep", "My Funded Futures": "MFFU", "MFFU": "MFFU", "Lucid": "Lucid"}
_FIRM_LINE = re.compile(r"^- \*\*The firm and account:\*\* (?P<firm>Topstep|My Funded Futures|MFFU|Lucid)\b", re.M)
_MARKET_LINE = re.compile(r"^- \*\*The market:\*\* (?P<market>[A-Z][A-Z0-9]{0,7})\b", re.M)
_SEARCH_MARKER = "**Declaration kind: design search.**"


class GoRefused(RuntimeError):
    """The log fails the go token's hygiene, or a membership rule refuses."""


def fences(text: str) -> tuple[list[bool], int | None]:
    """CommonMark's fenced code blocks, as `extended/reader.py` (Q-194d) reads them: for each line whether it is
    fenced (the fence lines included), and the index of a fence never closed (None when every fence closes)."""
    lines = text.splitlines()
    fenced, open_at, char, size = [False] * len(lines), None, "", 0
    for i, line in enumerate(lines):
        if open_at is None:
            m = _FENCE_OPEN.match(line)
            if m and not (m["fence"][0] == "`" and "`" in m["info"]):
                open_at, char, size = i, m["fence"][0], len(m["fence"])
                fenced[i] = True
            continue
        fenced[i] = True
        if re.fullmatch(rf" {{0,3}}{re.escape(char)}{{{size},}}[ \t]*", line):
            open_at = None
    return fenced, open_at


def _first_pins(lines: list[str], fenced: list[bool]) -> dict[str, tuple[int, str]]:
    """{declaration: (line index, sha256)} of each declaration's first unfenced hash row."""
    out: dict[str, tuple[int, str]] = {}
    for i, line in enumerate(lines):
        if fenced[i] or not _ROW.match(line):
            continue
        for m in _PIN.finditer(line):
            out.setdefault(m["decl"], (i, m["sha"]))
    return out


def _scan(text: str):
    """(counted tokens [(index, row, decl, sha)], problems [(row or None, index, message)], voids {row: (void row,
    index)}, first pins, lines)."""
    lines = text.splitlines()
    fenced, unclosed = fences(text)
    pins = _first_pins(lines, fenced)
    problems, tokens, voids = [], [], {}
    if unclosed is not None:
        problems.append((None, -1, f"line {unclosed + 1}: a fenced block opened here is never closed"))
    for i, line in enumerate(lines):
        r, c = _ROW.match(line), _THIRD_CELL.match(line)
        if not (r and c):
            continue
        row = r["row"]
        start = _MARKS.match(line, c.end()).end()
        go_like = bool(_GO_LIKE.match(line, start))
        if fenced[i]:
            if go_like:
                problems.append((row, i, f"{row} (line {i + 1}): a go token inside a fenced block is never a token"))
            continue
        v = _VOID.match(line)
        if v:
            voids[v["target"]] = (row, i)
            continue
        if not go_like:
            continue
        m = GO_TOKEN.match(line)
        if not m:
            problems.append((row, i, f"{row} (line {i + 1}): go-like but not exactly `go: F-NN @ <its LF sha256> -- "
                                  "<text>` at the third cell's start"))
            continue
        pin = pins.get(m["decl"])
        if pin is None or pin[0] >= i:
            problems.append((row, i, f"{row}: a go token for {m['decl']} with no hash row strictly before it"))
        elif pin[1] != m["sha"]:
            problems.append((row, i, f"{row}: a go token for {m['decl']} at a sha256 that is not its pin's"))
        else:
            tokens.append((i, row, m["decl"], m["sha"]))
    return tokens, problems, voids, pins, lines


def go_problems(text: str) -> list[str]:
    """The go token's hygiene problems of a decision log, after voids; [] is clean."""
    tokens, problems, voids, pins, lines = _scan(text)
    counted = {row for _, row, _, _ in tokens}
    pin_rows = {_ROW.match(lines[i])["row"] for i, _ in pins.values()}
    protected = {(_ROW.match(ln) or {"row": None})["row"] for ln in lines if _PROTECTED.match(ln)}
    out = [msg for row, i, msg in problems if row is None or row not in voids or voids[row][1] <= i]
    for target, (row, _) in voids.items():
        if target in counted or target in pin_rows or target in protected:
            out.append(f"{row}: `heldout-void` names {target}, a counted token or a pin row, which a void never voids")
    return out


def go_tokens(text: str) -> list[tuple[str, str, str]]:
    """The counted go tokens, in log order: (row, declaration, sha256). Refuses (`GoRefused`) a log with a problem."""
    probs = go_problems(text)
    if probs:
        raise GoRefused("; ".join(probs))
    return [(row, decl, sha) for _, row, decl, sha in _scan(text)[0]]


def go_row_present(text: str, decl: str, sha: str) -> bool:
    """The survey runner's check (section 14 step 4): the log clean and a counted go token for `decl` at `sha`."""
    try:
        return any(d == decl and s == sha for _, d, s in go_tokens(text))
    except GoRefused:
        return False


def membership(text: str, scope: dict[str, str]) -> tuple[str | None, dict[str, str]]:
    """(the membership event's row id or None, {firm: its member declaration}). `scope` maps a declaration to its
    firm when it is an NQ design search of the three firms (`declared_scope`). Refuses a log with a go problem, and a
    second in-scope hash row for a firm before the event (R-1)."""
    tokens, _, _, _, lines = _scan(text)
    go_tokens(text)                                          # the hygiene first
    event = next(((i, row) for i, row, decl, _ in tokens if decl in scope), None)
    fenced, _ = fences(text)
    members: dict[str, str] = {}
    for decl, (i, _sha) in sorted(_first_pins(lines, fenced).items(), key=lambda kv: kv[1][0]):
        if decl not in scope or (event is not None and i >= event[0]):
            continue
        firm = scope[decl]
        if firm in members:
            raise GoRefused(f"{decl}: a second hash row for {firm} before the membership event (R-1)")
        members[firm] = decl
    return (event[1] if event else None), members


def declared_scope(root: Path, market: str = "NQ") -> dict[str, str]:
    """{declaration: firm} for every `prereg/F-NN_*.md` carrying the design-search marker at a line's start whose
    declared market field names `market` and whose firm line begins with one of the three firms."""
    out = {}
    for pth in sorted((Path(root) / "prereg").glob("F-*.md")):
        text = pth.read_text(encoding="utf-8")
        if not any(line.startswith(_SEARCH_MARKER) for line in text.splitlines()):
            continue
        mk, fm = _MARKET_LINE.search(text), _FIRM_LINE.search(text)
        if mk and fm and mk["market"] == market:
            out[pth.name.split("_")[0]] = FIRM_NAMES[fm["firm"]]
    return out
