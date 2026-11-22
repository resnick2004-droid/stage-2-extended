"""The design search's go token and the membership event it fixes (G-1, G-2, B-3, C-1 to C-3; E-257, E-259).

A design search's go row (`prereg/TEMPLATE_design_search.md`, section 14 step 4) carries, as the first text of the
row's third cell, the token

    | E-NNN | YYYY-MM-DD | go: F-NN @ <the declaration's LF sha256> -- runner <the runner commit, 40 hex> -- <text> |

in the reader's positional form (`extended/reader.py`'s `_HO_HEAD` and `_HO_TAIL`). **This module re-implements none
of the reader's log rules**: rows (`ROW`), pins (`PIN`), fences and their `heldout-void` recovery (`_fence_state`),
and the void token (`HELDOUT_TOKENS["void"]`) are the reader's own, imported. A token counts only when:

* it sits outside any fenced block, as the reader reads fences (HTML comments as the reader reads them: no rule of
  their own, n-d);
* it is in the exact form above;
* its sha256 is its declaration's first pin's (the first unfenced line carrying `` `prereg/F-NN_<slug>.md` sha256
  `<64 hex>` ``, as `tests/test_declarations_fixed.py` and the reader's `pins()` count a pin), on a line strictly
  before the go row;
* its declaration has no earlier closing row (`heldout-closed: F-NN @ <sha> -- <cause> -- <text>`) and no earlier
  counted go token (C-3).

**Hygiene problems** (`go_problems`), each refusing every membership reading while it stands:

* a fence left open (the reader's rule, cleared as the reader clears it: a later `heldout-void: E-NNN` naming the row
  just before the fence);
* an exact go token inside a fence, unless the reader's fence recovery covers it or a later void names its row;
* a row (the reader's `ROW`) whose third cell begins go-like (after spaces, backticks and emphasis marks, `go:` or
  `go=` in any case) but is not the exact token, unless a later void names it and it carries no pin (the reader's
  rule for a malformed held-out row);
* an exact go token at another sha, before or in its own pin's line, after its declaration's closing row, or a second
  one for its declaration.

A void naming a valid row -- a counted go token, a pin row or a valid held-out token -- is a no-op, as in the reader.

**The membership event** (H-1'; E-257) is the first counted go token of a declaration in scope: an NQ design search of
Topstep, My Funded Futures or Lucid, read from the declaration's declared market field and firm line in their exact
form (`declared_scope`), which refuses, fail closed, a design-search file whose fields do not parse exactly once (C-1).
A member is the one in-scope declaration of its firm whose first pin comes strictly before the event's line; a second
in-scope pin for a firm before the event is refused (R-1).

`go_row_present(decisions, decl, sha, root)` is the survey runner's check before it starts: the log clean, the
declaration's file at `root` hashing to `sha` with a decidable scope, a counted go token for it at `sha`, and no
finalists' or closing row of it yet. `go_runner` returns the runner commit the counted go row names (U-1).

Text only: this module reads `DECISIONS.md` and `prereg/` and nothing else."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from extended import reader as RD

__all__ = ["GO_TOKEN", "CLOSED_TOKEN", "GoRefused", "fences", "go_problems", "go_tokens", "go_runner",
           "go_row_present", "membership", "scope_problems", "declared_scope", "FIRMS"]

#: the go token: the reader's positional head and tail around the declaration, its sha256 and the runner sub-form
GO_TOKEN = re.compile(RD._HO_HEAD + r"go: (?P<decl>F-\d+) @ (?P<sha>[0-9a-f]{64}) -- runner (?P<runner>[0-9a-f]{40})"
                      + RD._HO_TAIL)
#: the closing row (the held-out template's one form)
CLOSED_TOKEN = re.compile(RD._HO_HEAD + r"heldout-closed: (?P<decl>F-\d+) @ (?P<sha>[0-9a-f]{64}) -- "
                          r"(?P<cause>[a-z-]+)" + RD._HO_TAIL)
_GO_LIKE = re.compile(r"go\s*[:=]", re.IGNORECASE)
_DECL = re.compile(r"prereg/(F-\d+)_")
#: the declared fields' exact forms (C-1): a bare upper-case market code; a firm field one of the names below
_MARKET_FIELD = "- **The market:**"
_MARKET_LINE = re.compile(r"- \*\*The market:\*\* (?P<market>[A-Z][A-Z0-9]{0,7})(?: -- |$)")
_FIRM_FIELD = "- **The firm and account:**"
_FIRM_LINE = re.compile(r"- \*\*The firm and account:\*\* (?P<firm>.*?)(?:, | -- |$)")
FIRMS = {"Topstep": "Topstep", "My Funded Futures": "MFFU", "My Funded Futures (MFFU)": "MFFU", "MFFU": "MFFU",
         "Lucid": "Lucid"}
_FIRM_NAMES = re.compile(r"topstep|funded futures|mffu|lucid", re.IGNORECASE)
#: NQ and MNQ are one underlying (the design note's N-4): either is NQ's scope
_NQ = {"NQ", "MNQ"}
_SEARCH_MARKER = "**Declaration kind: design search.**"
_SEARCH_HEADINGS = ("## 5. The zero-edge convention", "## 6. The survey", "## 7. The pinning row")


class GoRefused(RuntimeError):
    """The log fails the go token's hygiene, a declaration's scope cannot be decided, or a membership rule refuses."""


def fences(text: str) -> tuple[list[bool], int | None, set[int]]:
    """The reader's fences with its `heldout-void` recovery (`extended.reader._fence_state`), unchanged."""
    return RD._fence_state(text)


def _first_pins(lines: list[str], fenced: list[bool]) -> dict[str, list[tuple[int, str]]]:
    """{declaration: [(line index, sha256), ...]} of every unfenced pin line, in file order (the reader's `PIN`)."""
    out: dict[str, list[tuple[int, str]]] = {}
    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        for rel, sha in RD.PIN.findall(line):
            m = _DECL.match(rel)
            if m:
                out.setdefault(m.group(1), []).append((i, sha))
    return out


def _scan(text: str) -> dict:
    lines = text.splitlines()
    fenced, unclosed, voided = fences(text)
    pins = _first_pins(lines, fenced)
    voids: dict[str, int] = {}
    for t in RD.heldout_tokens(text, "void"):
        voids.setdefault(t.get("target"), t.pos)
    closed: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = None if fenced[i] else CLOSED_TOKEN.match(line)
        if m:
            closed.setdefault(m["decl"], i)
    problems, tokens, seen = [], [], set()

    def voided_later(row: str, i: int) -> bool:
        return voids.get(row, -1) > i

    if unclosed is not None:
        problems.append(f"line {unclosed + 1}: a fenced block opened here is never closed")
    for i, line in enumerate(lines):
        r = RD.ROW.match(line)
        c = RD._HO_THIRD_CELL.match(line) if r else None
        if not c:
            continue
        row = r.group(1)
        go_like = bool(_GO_LIKE.match(line, RD._HO_MARKS.match(line, c.end()).end()))
        if fenced[i]:
            if GO_TOKEN.match(line) and i not in voided and not voided_later(row, i):
                problems.append(f"{row} (line {i + 1}): a go token inside a fenced block is never a token")
            continue
        if not go_like:
            continue
        m = GO_TOKEN.match(line)
        if not m:
            if not (voided_later(row, i) and not RD.PIN.search(line)):
                problems.append(f"{row} (line {i + 1}): go-like but not exactly `go: F-NN @ <its LF sha256> -- runner "
                                "<40 hex> -- <text>` at the third cell's start")
            continue
        decl, sha = m["decl"], m["sha"]
        first = pins.get(decl, [None])[0]
        if first is None or first[0] >= i:
            problems.append(f"{row}: a go token for {decl} with no pin strictly before it")
        elif first[1] != sha:
            problems.append(f"{row}: a go token for {decl} at a sha256 that is not its first pin's")
        elif closed.get(decl, len(lines)) < i:
            problems.append(f"{row}: a go token for {decl} after its closing row")
        elif decl in seen:
            problems.append(f"{row}: a second go token for {decl}")
        else:
            seen.add(decl)
            tokens.append((i, row, decl, sha, m["runner"]))
    return {"lines": lines, "fenced": fenced, "pins": pins, "closed": closed, "problems": problems, "tokens": tokens}


def go_problems(text: str) -> list[str]:
    """The go token's hygiene problems of a decision log; [] is clean."""
    return _scan(text)["problems"]


def go_tokens(text: str) -> list[tuple[str, str, str]]:
    """The counted go tokens, in log order: (row, declaration, sha256). Refuses (`GoRefused`) a log with a problem."""
    s = _scan(text)
    if s["problems"]:
        raise GoRefused("; ".join(s["problems"]))
    return [(row, decl, sha) for _, row, decl, sha, _ in s["tokens"]]


def go_runner(text: str, decl: str, sha: str) -> str | None:
    """The runner commit the declaration's counted go row names (U-1), or None. Refuses a log with a problem."""
    s = _scan(text)
    if s["problems"]:
        raise GoRefused("; ".join(s["problems"]))
    return next((runner for _, _, d, h, runner in s["tokens"] if d == decl and h == sha), None)


def _declaration_file(root: Path, decl: str) -> Path | None:
    hits = sorted((Path(root) / "prereg").glob(f"{decl}_*.md"))
    return hits[0] if len(hits) == 1 else None


def go_row_present(text: str, decl: str, sha: str, root: Path) -> bool:
    """The survey runner's check (section 14 step 4): the log clean; the declaration's one file at `root` hashing to
    `sha` (its LF text) with a decidable scope; a counted go token for it at `sha`; and no finalists' or closing row of
    it yet (C-3)."""
    s = _scan(text)
    if s["problems"]:
        return False
    f = _declaration_file(root, decl)
    if f is None or hashlib.sha256(f.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != sha:
        return False
    if scope_problems(f.read_text(encoding="utf-8")):
        return False
    if decl in s["closed"] or any(t.get("decl") == decl for t in RD.heldout_tokens(text, "finalists")):
        return False
    return any(d == decl and h == sha for _, _, d, h, _ in s["tokens"])


def membership(text: str, scope: dict[str, str]) -> tuple[str | None, dict[str, str]]:
    """(the membership event's row id or None, {firm: its member declaration}). `scope` maps a declaration to its firm
    when it is an NQ design search of the three firms (`declared_scope`). Refuses a log with a go problem, and a second
    in-scope pin for a firm before the event (R-1)."""
    s = _scan(text)
    if s["problems"]:
        raise GoRefused("; ".join(s["problems"]))
    event = next(((i, row) for i, row, decl, _, _ in s["tokens"] if decl in scope), None)
    members: dict[str, str] = {}
    for decl, rows in sorted(s["pins"].items(), key=lambda kv: kv[1][0][0]):
        i = rows[0][0]
        if decl not in scope or (event is not None and i >= event[0]):
            continue
        firm = scope[decl]
        if firm in members:
            raise GoRefused(f"{decl}: a second pin for {firm} before the membership event (R-1)")
        members[firm] = decl
    return (event[1] if event else None), members


def scope_problems(text: str) -> list[str]:
    """C-1: why a design-search file's scope cannot be decided ([] when it can, or when the file is no design search).
    A file is a design search when it carries the design-search marker at a line's start or a design search's
    headings; it must then carry the marker, and exactly one unfenced market line and one unfenced firm line in their
    exact forms."""
    lines = text.splitlines()
    fenced, _, _ = RD._fence_state(text)
    live = [ln for i, ln in enumerate(lines) if not fenced[i]]
    marked = any(ln.startswith(_SEARCH_MARKER) for ln in live)
    if not marked and not any(h in ln for ln in live for h in _SEARCH_HEADINGS):
        return []
    out = [] if marked else ["a design search's headings without the design-search marker at a line's start"]
    markets = [ln for ln in live if ln.startswith(_MARKET_FIELD)]
    if len(markets) != 1 or not _MARKET_LINE.match(markets[0]):
        out.append(f"the market field is not exactly one line `{_MARKET_FIELD} <MARKET> -- ...` ({len(markets)} found)")
    firms = [ln for ln in live if ln.startswith(_FIRM_FIELD)]
    if len(firms) != 1:
        out.append(f"the firm line is not exactly one line ({len(firms)} found)")
    else:
        name = _FIRM_LINE.match(firms[0])["firm"]
        if name not in FIRMS and _FIRM_NAMES.search(name):
            out.append(f"the firm field {name!r} names a firm of the line but not in its exact form")
    return out


def _scope_of(text: str, market: str) -> str | None:
    lines = text.splitlines()
    fenced, _, _ = RD._fence_state(text)
    live = [ln for i, ln in enumerate(lines) if not fenced[i]]
    mk = next(_MARKET_LINE.match(ln) for ln in live if ln.startswith(_MARKET_FIELD))
    name = _FIRM_LINE.match(next(ln for ln in live if ln.startswith(_FIRM_FIELD)))["firm"]
    wanted = _NQ if market == "NQ" else {market}
    return FIRMS.get(name) if mk["market"] in wanted else None


def declared_scope(root: Path, market: str = "NQ") -> dict[str, str]:
    """{declaration: firm} for every design-search `prereg/F-NN_*.md` of `market` and one of the three firms.
    Refuses (`GoRefused`, fail closed) when any design-search file's scope cannot be decided (`scope_problems`)."""
    out, bad = {}, []
    for pth in sorted((Path(root) / "prereg").glob("F-*.md")):
        text = pth.read_text(encoding="utf-8")
        probs = scope_problems(text)
        if probs:
            bad.append(f"{pth.name}: {'; '.join(probs)}")
            continue
        if not any(ln.startswith(_SEARCH_MARKER) for ln in text.splitlines()):
            continue
        firm = _scope_of(text, market)
        if firm:
            out[pth.name.split("_")[0]] = firm
    if bad:
        raise GoRefused("; ".join(bad))
    return out
