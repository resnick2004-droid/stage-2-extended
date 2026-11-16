"""The one door to Stage 2's bars and walks, and the judged block's seal (Q-32; the Phase 0 audit's R-4, R-5 and H-2,
`docs/audits/phase0/D_protocol.md`; family B's red team m-7; E-019).

    from extended import reader
    bars = reader.read_bars("2020-01-02", "2023-12-29")                         # the choice block: no tag needed
    bars = reader.read_bars("2024-01-02", "2026-07-16", purpose="stage_C_judgement",
                            declaration="prereg/F-11_name.md", what="F-11 stage C: the pick's brackets")
    walks = reader.read_walks("A3", "walks", "2024-01-02", "2026-07-16", purpose=..., declaration=...)
    reader.authorise_engine_read("2020-01-02", "2026-07-16", purpose="identity", declaration="E-004",
                                 files=[...], what="E-004's identity")         # before Stage 2's engine reads itself

**Why.** "The judged block is read once, by a pinned declaration, for a declared purpose" was a promise; this module
makes it a mechanism. A look at the judged block before the pick is frozen does not announce itself -- the numbers
still compute -- so every read of Stage 2's bars (`vendor/stage2/data/bars/<ROOT>/bars.parquet`) and walks
(`vendor/stage2/data/atlas/<family>/<table>.parquet`) by this repository's code comes through here, and a read the
rules do not allow raises **before anything is read** (`tests/test_reader.py` scans this repository's code for any
other parquet read).

**The blocks** (feature-rules section 4; CLAUDE.md "Windows"): the **choice block** 2020-01-02 to 2023-12-29 and the
**judged block** 2024-01-02 to 2026-07-16. The seal starts the day after the choice block ends, so the holiday gap
(2023-12-30 to 2024-01-01) is under it. **Anything from 2026-07-17 is refused outright, whatever the purpose** (NQ's
declared confirmation window; it is not on disk; refused anyway, `ConfirmationWindowRefused`), and so is anything
before 2020-01-02. Stage 2's own guard runs as well: bars come through the vendored `propedge.data.bars.read_bars`
(its `assert_readable` for the purpose `development`), and walks after the same `assert_readable`, so the vendored
`config/windows.yaml` refuses NQ's reserve independently.

**The rules for a read touching the judged block** (`JudgedBlockSealed` otherwise), checked in this order:

1. it declares a `purpose` -- a plain name such as `stage_C_judgement` or `identity` (letters, digits, underscores);
2. **`identity`** -- the identities that must read Stage 2's whole window (E-004, E-010, E-011, E-024, E-028): the
   declaration is the decision row of the identity (`"E-004"`), which must exist in `DECISIONS.md` and mention an
   identity, and the process's script must be one of this repository's identity scripts (`identity/*.py`). Allowed
   in any tree, as often as it runs, and checked wherever it runs; **ledgered only inside a clean run** (E-026, the
   lead's rule: `S2X_CLEAN_RUN` set -- and then the tree must be that run's checkout of a committed tree, with its
   run id, as a family read's must), so a worktree's or the suite's identity runs write nothing (Q-48);
2a. **`registered_design`** -- re-reading Stage 2's own registered designs, already judged in Stage 2 (E-037, Q-58):
   the readings scripts beside them (Q-17's `scripts/user_beside.py`, Q-20's `scripts/breakeven_fidelity.py`, Q-18's
   `scripts/p14_validation.py`). `design=` names the designs read, each one of `REGISTERED_DESIGNS` (P-14, P-15,
   P-16; nothing else, on either block); the declaration is a decision row that exists and names each of them
   (never a family's or a described reading's file: a family can never use this purpose, whatever its line says);
   the process's script must be one of this repository's `scripts/*.py`. Checked wherever it runs and ledgered only
   inside a clean run, exactly as an identity's read; never limited to once;
3. every other purpose: a purpose containing a choice or fitting word (`choose`, `choice`, `fit`, `select`, `search`,
   `tune`, `train`, ...) never reads the judged block, whatever a declaration says (the audit's H-2); the declaration
   is a family file `prereg/F-NN_<name>.md` (or its id `F-NN`) or a described reading's `prereg/RD-NN_<name>.md` (or
   `RD-NN`; E-023 (1), E-025 (1), Q-58: on exactly the same rules) that exists, is **pinned** -- its sha256 (of the LF
   text) in a decision row, read exactly as `tests/test_declarations_fixed.py` reads the pins -- and still hashes to
   that pin, and whose text **names the purpose for the judged block** on a line of the form

       - **Judged-block reads:** `stage_C_judgement`, `stage_D_scorecard`

   (a line starting, after list or quote markers, with "Judged-block reads", a colon, and each purpose in backticks;
   a purpose named in prose elsewhere authorises nothing);
4. it runs **inside a clean run** -- the checkout `scripts/run_clean.py` made under `%LOCALAPPDATA%/stage2-extended-
   runs/<name>`, named by `S2X_CLEAN_RUN`, with the run id `S2X_RUN_ID` -- of a **committed** tree (no uncommitted
   change outside `results/`): a judged read is made by a named commit, as a result is (CLAUDE.md "Results");
5. **once**: if the ledger already holds a read of the same declaration and purpose by another run, the read is
   refused (`JudgedBlockReadTwice`) unless `repeat="E-NNN"` names a decision row that names the declaration -- one
   row, one more run. One run may read as often as it needs (bars, then walks; its own workers share the run id).

**The read ledger** (`results/read_ledger.jsonl` of the tree whose declarations authorise the read): every family's
or described reading's read touching the judged block, and every identity's or registered design's read inside a clean
run (`Authorisation.ledgered`), appends one line **before the data is read** (a ledger that cannot be written means no
read) -- who (the script, its arguments, the calling function, the commit, the dirty flag, the process, the clean run
and run id), what (each file with its sha256, size and whether it matches `vendor/DATA_MANIFEST_stage2.sha256`; the
columns; the description), which dates (the span, the blocks, the judged part), which declaration (its path or row,
its sha256, its kind -- `family`, `described_reading`, `identity`, `registered_design` -- and a registered design's
`designs`) and purpose, and when (UTC). Choice-block reads are not ledgered (the brief: judged reads only). The
ledger is append-only: a line that does not parse, or a file that does not end in a newline, refuses the next read
(`LedgerError`); `ledger_history_problems` reports any line committed in the history that is no longer in HEAD, or in
HEAD that is no longer in the working copy (`tests/test_reader.py` runs it on this repository); the hook
`scripts/hooks/protect_results.py` warns on any tool edit that changes an existing line; `scripts/run_clean.py
--collect` brings a run's new lines home as a union (Q-67): only when the run only appended to its commit's ledger and
this tree's has lost no line, the result verified by `read_ledger` before it replaces this tree's.

**What it does not do.** It cannot see a read made inside a vendored call (Stage 2's engine opens the bars and the
atlas itself in the identities and the U1 replay) -- such a runner calls `authorise_engine_read` with the files the
engine will open, which checks and ledgers exactly as a read here does (every identity's `main` does, Q-48); nor a
script that opens the files by hand
(the scan in the tests is a deterrent for this repository's committed code, not proof). Withdrawn families are not
machine-readable yet (the audit's R-8 registry): a withdrawn family's pinned file authorises a read if it names the
purpose on its line -- F-01 names none.

Importing this module touches no `sys.path` and imports no engine; the vendored tree is put on the path
(`extended.use_vendored_stage2`) only when bars or walks are actually read, so run reads in a process of their own.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

from extended import CLEAN_RUN_ENV, ROOT, RUN_ID_ENV, RUNS_DIR

#: the choice block (feature-rules section 4): every choice, fit and search
CHOICE_START, CHOICE_END = date(2020, 1, 2), date(2023, 12, 29)
#: the judged block: one read of a frozen pick, by a pinned declaration
JUDGED_START, JUDGED_END = date(2024, 1, 2), date(2026, 7, 16)
#: NQ's declared confirmation window opens here (Stage 2 `config/windows.yaml`, reserved): never read
CONFIRMATION_START = date(2026, 7, 17)
#: the seal covers every day after the choice block (the holiday gap before JUDGED_START included)
SEAL_START = CHOICE_END + timedelta(days=1)

IDENTITY = "identity"
#: re-reading Stage 2's own registered, already-judged designs (E-037, Q-58), only these
REGISTERED_DESIGN = "registered_design"
REGISTERED_DESIGNS = ("P-14", "P-15", "P-16")
LEDGER_REL = "results/read_ledger.jsonl"
LEDGER_VERSION = 1
LEDGER_KEYS = ("ledger", "when", "who", "what", "dates", "declaration", "purpose", "repeat")
VENDOR_REL = "vendor/stage2"
STORE_REL = "vendor/stage2/data/bars"
ATLAS_REL = "vendor/stage2/data/atlas"
DATA_MANIFEST_REL = "vendor/DATA_MANIFEST_stage2.sha256"

#: words that mark a purpose as choosing or fitting: such a purpose never reads the judged block (the audit's H-2)
CHOICE_WORDS = frozenset({"choose", "choice", "fit", "fitting", "select", "selection", "search", "tune", "tuning",
                          "train", "training"})
PURPOSE = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}")
#: the declared line: "Judged-block reads[ anything]: `purpose`, `purpose`" at a line's start (after markers)
DECLARED_LINE = re.compile(r"^[ \t>*_\-]*judged-block reads\b[^:\n]*:(.*)$", re.IGNORECASE | re.MULTILINE)
PURPOSE_TOKEN = re.compile(r"`([A-Za-z][A-Za-z0-9_]*)`")
#: a pin, exactly as tests/test_declarations_fixed.py reads it: a family's (`F-nn`) or a described reading's (`RD-nn`)
PIN = re.compile(r"`(prereg/(?:F|RD)-\d+[^`]*\.md)` sha256 `([0-9a-f]{64})`")
ROW = re.compile(r"\|\s*(E-\d+)\s*\|")
DECLARATION_PATH = re.compile(r"prereg/(?:F|RD)-\d+[^/`]*\.md")
#: a declaration's id: a family's `F-nn` or a described reading's `RD-nn`
F_ID = re.compile(r"(?:F|RD)-\d+")
DECLARATION_ID = re.compile(r"prereg/((?:F|RD)-\d+)")
E_ID = re.compile(r"E-\d+")
NAME = re.compile(r"[A-Za-z0-9_]+")
THIS_FILE = Path(__file__).resolve()


class ReadRefused(RuntimeError):
    """A read of Stage 2's bars or walks this module does not allow; raised before anything is read."""


class ConfirmationWindowRefused(ReadRefused):
    """The span reaches 2026-07-17 or later: NQ's confirmation window, refused whatever the purpose."""


class JudgedBlockSealed(ReadRefused):
    """The span reaches the judged block without a purpose and a declaration that allow it."""


class JudgedBlockReadTwice(JudgedBlockSealed):
    """Another run already read the judged block under this declaration and purpose."""


class LedgerError(ReadRefused):
    """The read ledger does not verify or cannot be written, or the commit cannot be named: no judged read."""


@dataclass(frozen=True)
class Authorisation:
    """What a read was allowed to touch, and under what."""
    start: date
    end: date
    blocks: tuple[str, ...]
    judged: bool
    judged_first: date | None
    judged_last: date | None
    purpose: str | None
    declaration: str | None
    declaration_sha256: str | None
    #: "family" | "described_reading" | "identity" | "registered_design" | None (a choice-block read)
    kind: str | None
    repeat: str | None
    #: whether the read appends its line to the ledger: every family's or described reading's judged read; an
    #: identity's or a registered design's only inside a clean run (E-026, E-037); never a choice-block read
    ledgered: bool = False
    #: the registered designs a `registered_design` read re-reads, in `REGISTERED_DESIGNS`' order (else empty)
    designs: tuple[str, ...] = ()


# ------------------------------------------------------------------------------------------------- dates and blocks


def _day(x: Any) -> date:
    if isinstance(x, datetime):                         # a pandas Timestamp is a datetime
        return x.date()
    if isinstance(x, date):
        return x
    if isinstance(x, str):
        try:
            return date.fromisoformat(x)
        except ValueError:
            return datetime.fromisoformat(x).date()
    raise TypeError(f"a day is a date, a datetime or an ISO string, not {type(x).__name__} {x!r}")


def span(start: Any, end: Any, what: str = "read") -> tuple[date, date]:
    """`(start, end)` as days, refused when it reaches the confirmation window (first) or starts before the choice
    block; `ValueError` when it ends before it starts."""
    s, e = _day(start), _day(end)
    if max(s, e) >= CONFIRMATION_START:
        raise ConfirmationWindowRefused(
            f"REFUSED: {what} {s} to {e} reaches {CONFIRMATION_START} or later -- NQ from {CONFIRMATION_START} is the "
            "declared confirmation window (CLAUDE.md 'Windows'; Stage 2 config/windows.yaml, reserved), never read "
            "until a carried candidate is registered, whatever the purpose or declaration")
    if e < s:
        raise ValueError(f"{what}: {e} is before {s}")
    if s < CHOICE_START:
        raise ReadRefused(f"REFUSED: {what} starts {s}, before the development window opens on {CHOICE_START} "
                          "(CLAUDE.md 'Windows': development NQ 2020-01-02 to 2026-07-16 only)")
    return s, e


def blocks_of(start: Any, end: Any) -> tuple[str, ...]:
    """The blocks a span touches: ("choice",), ("judged",) or ("choice", "judged")."""
    s, e = span(start, end)
    return tuple(b for b, on in (("choice", s <= CHOICE_END), ("judged", e >= SEAL_START)) if on)


def check_returned(days: Iterable[Any], start: Any, end: Any) -> None:
    """After a read: every returned day lies inside what was authorised, and none on or after 2026-07-17."""
    s, e = _day(start), _day(end)
    got = {_day(d) for d in days}
    late = sorted(d for d in got if d >= CONFIRMATION_START)
    if late:
        raise ConfirmationWindowRefused(f"REFUSED: the read returned {len(late)} day(s) from {late[0]} on -- the "
                                        f"confirmation window opens {CONFIRMATION_START}; nothing is returned")
    out = sorted(d for d in got if d < s or d > e)
    if out:
        raise ReadRefused(f"REFUSED: the read returned day(s) outside {s} to {e} ({out[:3]}); nothing is returned")


# ---------------------------------------------------------------------------------------------------- declarations


def declared_purposes(text: str) -> frozenset[str]:
    """The purposes a declaration names for the judged block: the backticked names on its 'Judged-block reads:'
    lines."""
    return frozenset(p for m in DECLARED_LINE.finditer(text) for p in PURPOSE_TOKEN.findall(m.group(1)))


def pins(decisions_text: str) -> dict[str, set[str]]:
    """{`prereg/F-..md` or `prereg/RD-..md`: {sha256, ...}} from the decision log, as
    `tests/test_declarations_fixed.py` reads it."""
    out: dict[str, set[str]] = {}
    for rel, h in PIN.findall(decisions_text):
        out.setdefault(rel, set()).add(h)
    return out


def decision_row(decisions_text: str, row_id: str) -> str | None:
    """The decision log's line for `row_id` (`E-NNN`), or None."""
    for line in decisions_text.splitlines():
        m = ROW.match(line)
        if m and m.group(1) == row_id:
            return line
    return None


def sha256_lf(p: Path) -> str:
    """The sha256 of a text file's LF form (the pins are of the LF text, E-003)."""
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _decisions(repo: Path) -> str:
    p = repo / "DECISIONS.md"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _rel(p: Path, repo: Path) -> str | None:
    for base in (repo, ROOT):
        try:
            return Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(base))).as_posix()
        except ValueError:
            continue
    return None


def _family_ref(declaration: Any, repo: Path, what: str) -> str:
    s = str(declaration).replace("\\", "/")
    if F_ID.fullmatch(s):
        found = sorted(repo.glob(f"prereg/{s}_*.md")) + ([repo / "prereg" / f"{s}.md"]
                                                         if (repo / "prereg" / f"{s}.md").is_file() else [])
        if not found:
            raise JudgedBlockSealed(f"REFUSED: {what}: the declaration {s} does not exist (no prereg/{s}_*.md)")
        if len(found) > 1:
            raise JudgedBlockSealed(f"REFUSED: {what}: {s} names {len(found)} files; name the one by its path")
        return f"prereg/{found[0].name}"
    if Path(s).is_absolute():
        s = _rel(Path(s), repo) or s
    if not DECLARATION_PATH.fullmatch(s):
        raise JudgedBlockSealed(f"REFUSED: {what}: a judged-block read serves a family's or a described reading's "
                                "declaration, a file prereg/F-NN_<name>.md or prereg/RD-NN_<name>.md of this repository "
                                f"(pinned by its decision row), not {s!r}")
    if not (repo / s).is_file():
        raise JudgedBlockSealed(f"REFUSED: {what}: the declaration {s} does not exist in {repo}")
    return s


# ---------------------------------------------------------------------------------------------- process and git


def _main_script() -> Path | None:
    """The process's script (`__main__.__file__`), None for `python -c` or an interactive session."""
    f = getattr(sys.modules.get("__main__"), "__file__", None)
    return Path(f).resolve() if f else None


def _under(p: Path | None, d: Path) -> bool:
    if p is None:
        return False
    a, b = os.path.normcase(os.path.abspath(p)), os.path.normcase(os.path.abspath(d))
    return a.startswith(b.rstrip("\\/") + os.sep)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def _commit(repo: Path, what: str) -> str:
    r = _git(repo, "rev-parse", "HEAD")
    if r.returncode or not r.stdout.strip():
        raise LedgerError(f"REFUSED: {what}: the commit of {repo} cannot be named ({r.stderr.strip()[:200]}); a "
                          "judged-block read records the commit that made it")
    return r.stdout.strip()


def _dirty(repo: Path) -> list[str]:
    """Tracked files changed outside `results/` (a run's own output is not code)."""
    r = _git(repo, "status", "--porcelain", "--untracked-files=no", "--", ".", ":(exclude)results")
    if r.returncode:
        raise LedgerError(f"REFUSED: git status failed in {repo}: {r.stderr.strip()[:200]}")
    return [line[3:] for line in r.stdout.splitlines() if len(line) > 3]


def _run() -> tuple[str | None, str | None]:
    return os.environ.get(CLEAN_RUN_ENV) or None, os.environ.get(RUN_ID_ENV) or None


def _sanitise(text: str, repo: Path) -> str:
    for base, mark in ((repo, "."), (ROOT, "."), (Path.home(), "~")):
        for form in {str(base), str(base).replace("\\", "/")}:
            if form and form in text:
                text = text.replace(form, mark)
    return text


def _caller(repo: Path) -> str:
    f = sys._getframe(1)
    while f is not None and Path(f.f_code.co_filename).resolve() == THIS_FILE:
        f = f.f_back
    if f is None:
        return "?"
    name = f.f_code.co_filename
    rel = _rel(Path(name), repo) if not name.startswith("<") else None
    return f"{rel or _sanitise(name, repo)}:{f.f_lineno}:{f.f_code.co_name}"


# ---------------------------------------------------------------------------------------------------- authorisation


def _check_purpose(purpose: Any) -> None:
    if not isinstance(purpose, str) or not PURPOSE.fullmatch(purpose):
        raise ValueError(f"a purpose is a plain name (a letter, then letters, digits or underscores, at most 64), "
                         f"such as 'stage_C_judgement' or 'identity'; not {purpose!r}")


def _choice_purpose(purpose: str) -> bool:
    return any(t in CHOICE_WORDS for t in purpose.lower().split("_"))


def _identity(declaration: Any, repo: Path, what: str) -> str:
    script = _main_script()
    if not _under(script, repo / "identity"):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: the purpose 'identity' reads the judged block only from this repository's identity "
            f"scripts (identity/*.py); this process's script is {script or 'none (python -c or an interactive one)'}")
    if declaration is None or not E_ID.fullmatch(str(declaration)):
        raise JudgedBlockSealed(f"REFUSED: {what}: an identity read names the decision row of its identity "
                                f"(declaration='E-NNN', e.g. 'E-004'), not {declaration!r}")
    row = decision_row(_decisions(repo), str(declaration))
    if row is None:
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration} is no decision row of {repo / 'DECISIONS.md'}")
    if "identit" not in row.lower():
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration}'s row does not mention an identity")
    return str(declaration)


def names_design(row: str, design: str) -> bool:
    """Whether a decision row names a registered design (`P-14`, not `P-140` or `XP-14`)."""
    return re.search(rf"(?<![\w-]){re.escape(design)}(?!\d)", row) is not None


def _designs(design: Any, what: str) -> tuple[str, ...]:
    """`design=` as the registered designs it names, in `REGISTERED_DESIGNS`' order; refused unless every name is one
    of them and there is at least one."""
    names = [design] if isinstance(design, str) else list(design) if isinstance(design, (list, tuple, set,
                                                                                        frozenset)) else None
    if not names:
        raise JudgedBlockSealed(f"REFUSED: {what}: the purpose {REGISTERED_DESIGN!r} names the registered design(s) it "
                                f"re-reads (design='P-14' or a list of {', '.join(REGISTERED_DESIGNS)}), not {design!r}")
    bad = [d for d in names if d not in REGISTERED_DESIGNS]
    if bad:
        raise JudgedBlockSealed(f"REFUSED: {what}: {bad[0]!r} is not a registered design this purpose re-reads -- only "
                                f"Stage 2's own judged designs {', '.join(REGISTERED_DESIGNS)} (E-037)")
    return tuple(d for d in REGISTERED_DESIGNS if d in names)


def _registered(declaration: Any, designs: tuple[str, ...], repo: Path, what: str) -> str:
    script = _main_script()
    if not _under(script, repo / "scripts"):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: the purpose {REGISTERED_DESIGN!r} re-reads Stage 2's registered designs only from this "
            f"repository's readings scripts (scripts/*.py, E-037); this process's script is "
            f"{script or 'none (python -c or an interactive one)'}")
    if declaration is None or not E_ID.fullmatch(str(declaration)):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: a registered design's re-read names the decision row that admits it "
            f"(declaration='E-NNN'), never a family's or a described reading's file; not {declaration!r}")
    row = decision_row(_decisions(repo), str(declaration))
    if row is None:
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration} is no decision row of {repo / 'DECISIONS.md'}")
    missing = [d for d in designs if not names_design(row, d)]
    if missing:
        raise JudgedBlockSealed(f"REFUSED: {what}: {declaration}'s row does not name {', '.join(missing)}; a "
                                "registered design is re-read under a row that names it")
    return str(declaration)


def _family(declaration: Any, purpose: str, repo: Path, what: str) -> tuple[str, str]:
    if _choice_purpose(purpose):
        raise JudgedBlockSealed(
            f"REFUSED: {what}: {purpose!r} is a choice or fitting purpose, and the judged block is sealed during "
            "choice and fitting (the audit's R-4, H-2): choose, fit and search on the choice block 2020-01-02 to "
            "2023-12-29")
    if declaration is None:
        raise JudgedBlockSealed(f"REFUSED: {what}: a read of the judged block for {purpose!r} names no declaration "
                                "(declaration='prereg/F-NN_<name>.md' or 'prereg/RD-NN_<name>.md', pinned, naming the "
                                "purpose)")
    ref = _family_ref(declaration, repo, what)
    sha = sha256_lf(repo / ref)
    pinned = pins(_decisions(repo)).get(ref)
    if not pinned:
        raise JudgedBlockSealed(f"REFUSED: {what}: {ref} is not pinned -- no decision row of DECISIONS.md carries its "
                                "sha256 (a declaration is pinned by the lead's row before any judged read)")
    if pinned != {sha}:
        raise JudgedBlockSealed(f"REFUSED: {what}: {ref} was edited since its pin (its sha256 {sha[:12]} is not the "
                                f"pinned {sorted(h[:12] for h in pinned)}); a change is a new family (or reading)")
    if purpose not in declared_purposes((repo / ref).read_text(encoding="utf-8")):
        raise JudgedBlockSealed(f"REFUSED: {what}: {ref} does not name {purpose!r} on its 'Judged-block reads:' line "
                                "(a purpose named elsewhere in the text authorises nothing)")
    return ref, sha


def _clean_run(repo: Path, what: str) -> None:
    name, run_id = _run()
    if not name:
        raise JudgedBlockSealed(f"REFUSED: {what}: a family's or a described reading's judged-block read runs only "
                                f"inside a clean run (python scripts/run_clean.py), and {CLEAN_RUN_ENV} is not set")
    want = Path(RUNS_DIR) / name
    if os.path.normcase(os.path.abspath(repo)) != os.path.normcase(os.path.abspath(want)):
        raise JudgedBlockSealed(f"REFUSED: {what}: {CLEAN_RUN_ENV}={name!r} but this tree is {repo}, not that clean "
                                f"run's checkout {want}")
    if not run_id:
        raise JudgedBlockSealed(f"REFUSED: {what}: the clean run has no {RUN_ID_ENV} (scripts/run_clean.py sets it "
                                "for each run; the once-rule tells runs apart by it)")
    bad = _dirty(repo)
    if bad:
        raise JudgedBlockSealed(f"REFUSED: {what}: {repo} has uncommitted changes outside results/ ({bad[:5]}); a "
                                "judged-block read is made by a committed commit")


def _once(repo: Path, ref: str, purpose: str, repeat: str | None, what: str) -> None:
    _, run_id = _run()
    earlier = [r for r in read_ledger(ledger_path(repo))
               if (r.get("declaration") or {}).get("ref") == ref and r.get("purpose") == purpose]
    others = sorted({str((r.get("who") or {}).get("run_id")) for r in earlier} - {run_id})
    if repeat is not None:
        if not E_ID.fullmatch(str(repeat)):
            raise ValueError(f"repeat names a decision row 'E-NNN', not {repeat!r}")
        row = decision_row(_decisions(repo), str(repeat))
        fid = DECLARATION_ID.match(ref)
        if row is None or not (ref in row or (fid and re.search(rf"\b{fid.group(1)}\b", row))):
            raise JudgedBlockSealed(f"REFUSED: {what}: {repeat} does not name {ref}; a further judged read is "
                                    "authorised by a decision row naming the declaration")
        used = sorted({str((r.get("who") or {}).get("run_id")) for r in earlier
                       if r.get("repeat") == repeat} - {run_id})
        if used:
            raise JudgedBlockReadTwice(f"REFUSED: {what}: {repeat} already authorised the read of run {used[0]}; one "
                                       "row, one more run")
        return
    if others:
        raise JudgedBlockReadTwice(
            f"REFUSED: {what}: {ref} was read on the judged block for {purpose!r} by run(s) {others[:3]}; the judged "
            "block is read once -- a further read needs a decision row naming the declaration, passed as "
            "repeat='E-NNN' (the failure protocol: never rerun until it passes)")


def _exists(declaration: Any, repo: Path) -> bool:
    """A choice-block read's declaration, if it names one, exists: a decision row, an F- or RD-id, or a file of the
    tree."""
    s = str(declaration).replace("\\", "/")
    if E_ID.fullmatch(s):
        return decision_row(_decisions(repo), s) is not None
    if F_ID.fullmatch(s):
        return bool(list(repo.glob(f"prereg/{s}_*.md"))) or (repo / "prereg" / f"{s}.md").is_file()
    return (Path(s) if Path(s).is_absolute() else repo / s).is_file()


def authorise(start: Any, end: Any, *, purpose: str | None = None, declaration: Any = None,
              repeat: str | None = None, design: Any = None, repo: Path | str | None = None,
              what: str = "read") -> Authorisation:
    """Whether a read of `start` to `end` (trading days, inclusive) may happen, and under what; raises otherwise.
    Reads nothing and writes nothing. `repo` is the tree whose `DECISIONS.md`, `prereg/`, git state and ledger count
    (this repository's root; tests pass a temporary tree). `design` (a name or a list) belongs to the purpose
    `registered_design` only."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    s, e = span(start, end, what)
    if purpose is not None:
        _check_purpose(purpose)
    if design is not None and purpose != REGISTERED_DESIGN:
        raise ValueError(f"{what}: design= names Stage 2's registered designs for the purpose {REGISTERED_DESIGN!r} "
                         f"only, not for {purpose!r}")
    designs = _designs(design, what) if purpose == REGISTERED_DESIGN else ()
    blocks = blocks_of(s, e)
    if "judged" not in blocks:
        if declaration is not None and not _exists(declaration, tree):
            raise ReadRefused(f"REFUSED: {what}: the declaration {declaration!r} does not exist in {tree}")
        return Authorisation(s, e, blocks, False, None, None, purpose,
                             str(declaration) if declaration is not None else None, None, None, repeat, False,
                             designs)
    # the judged part as the judged block names it; a span inside the holiday gap alone keeps its own first day
    first = max(s, JUDGED_START) if e >= JUDGED_START else max(s, SEAL_START)
    head = f"{what} ({s} to {e}) reaches the judged block ({first} to {e})"
    if purpose is None:
        raise JudgedBlockSealed(f"REFUSED: {head} and declares no purpose. A choice-block read needs no tag; a "
                                "judged read declares its purpose and the pinned declaration that names it")
    if purpose == IDENTITY:
        ref = _identity(declaration, tree, head)
        inside = bool(_run()[0])                        # E-026: an identity's read is ledgered only in a clean run,
        if inside:                                      # and a clean run's marker is checked as a family read's is
            _clean_run(tree, head)
        return Authorisation(s, e, blocks, True, first, e, purpose, ref, None, "identity", repeat, inside)
    if purpose == REGISTERED_DESIGN:
        ref = _registered(declaration, designs, tree, head)
        inside = bool(_run()[0])                        # E-037: ledgered only in a clean run, exactly as an identity
        if inside:
            _clean_run(tree, head)
        return Authorisation(s, e, blocks, True, first, e, purpose, ref, None, REGISTERED_DESIGN, repeat, inside,
                             designs)
    ref, sha = _family(declaration, purpose, tree, head)
    _clean_run(tree, head)
    _once(tree, ref, purpose, repeat, head)
    kind = "described_reading" if ref.startswith("prereg/RD-") else "family"
    return Authorisation(s, e, blocks, True, first, e, purpose, ref, sha, kind, repeat, True)


# ------------------------------------------------------------------------------------------------------- the ledger


def ledger_path(repo: Path | str | None = None) -> Path:
    return (Path(repo).resolve() if repo is not None else ROOT) / LEDGER_REL


def read_ledger(path: Path | str) -> list[dict[str, Any]]:
    """Every line of a read ledger, verified: each a JSON object with the ledger's keys, the file ending in a newline.
    An absent or empty ledger is []."""
    p = Path(path)
    if not p.is_file():
        return []
    data = p.read_bytes()
    if not data:
        return []
    if not data.endswith(b"\n"):
        raise LedgerError(f"REFUSED: {p} does not end in a newline -- a line was cut or edited; the ledger is "
                          "append-only (no judged read until the lead has looked)")
    out = []
    for i, line in enumerate(data.decode("utf-8").split("\n")[:-1], 1):
        try:
            rec = json.loads(line)
        except ValueError:
            raise LedgerError(f"REFUSED: {p} line {i} is not JSON -- the ledger was edited") from None
        if not isinstance(rec, dict) or any(k not in rec for k in LEDGER_KEYS):
            raise LedgerError(f"REFUSED: {p} line {i} lacks the ledger's fields {LEDGER_KEYS}")
        out.append(rec)
    return out


def _data_manifest(repo: Path) -> dict[str, str]:
    p = repo / DATA_MANIFEST_REL
    if not p.is_file():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            out[parts[1].strip().lstrip("*")] = parts[0].lower()
    return out


def _file_entry(p: Path, repo: Path, manifest: dict[str, str]) -> dict[str, Any]:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    digest = h.hexdigest()
    rel = _rel(p, repo)
    try:
        in_vendor = Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(repo / VENDOR_REL))).as_posix()
    except ValueError:
        in_vendor = None
    want = manifest.get(in_vendor) if in_vendor else None
    return {"path": rel or _sanitise(str(p), repo), "sha256": digest, "bytes": p.stat().st_size,
            "in_data_manifest": None if want is None else want == digest}


def _record(a: Authorisation, kind: str, files: Sequence[Path], columns: list[str] | None, what: str,
            repo: Path) -> dict[str, Any]:
    """Append the read's one line to the ledger (before the data is read); raises `LedgerError` if it cannot."""
    commit = _commit(repo, what)
    clean, run_id = _run()
    script = _main_script()
    manifest = _data_manifest(repo)
    rec = {
        "ledger": LEDGER_VERSION,
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "who": {"script": (_rel(script, repo) or _sanitise(str(script), repo)) if script else None,
                "argv": [_sanitise(str(x), repo) for x in sys.argv[1:]], "caller": _caller(repo),
                "commit": commit, "dirty": bool(_dirty(repo)), "pid": os.getpid(), "clean_run": clean,
                "run_id": run_id},
        "what": {"kind": kind, "files": [_file_entry(Path(f), repo, manifest) for f in files], "columns": columns,
                 "description": what},
        "dates": {"start": a.start.isoformat(), "end": a.end.isoformat(), "blocks": list(a.blocks),
                  "judged_first": a.judged_first.isoformat() if a.judged_first else None,
                  "judged_last": a.judged_last.isoformat() if a.judged_last else None},
        "declaration": {"ref": a.declaration, "sha256": a.declaration_sha256, "kind": a.kind,
                        **({"designs": list(a.designs)} if a.designs else {})},
        "purpose": a.purpose,
        "repeat": a.repeat,
    }
    path = ledger_path(repo)
    read_ledger(path)                                   # a ledger that does not verify takes no new line
    data = (json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o644)
        try:
            if os.write(fd, data) != len(data):
                raise OSError("short write")
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError as exc:
        raise LedgerError(f"REFUSED: {what}: the read ledger {path} cannot be written ({exc}); no judged read "
                          "without its line") from None
    return rec


def missing_lines(old: str, new: str) -> list[str]:
    """The non-blank lines of `old` not found in `new`, counted with multiplicity (order not checked: a merge
    interleaves two branches' lines)."""
    have = Counter(new.splitlines())
    out = []
    for line in old.splitlines():
        if not line.strip():
            continue
        if have[line] > 0:
            have[line] -= 1
        else:
            out.append(line)
    return out


def ledger_history_problems(repo: Path | str | None = None, rel: str = LEDGER_REL) -> list[str]:
    """Every way the ledger lost a line: a line committed anywhere in HEAD's history that is not in HEAD, and a line
    of HEAD's that is not in the working copy. [] when the ledger only ever grew (or never existed)."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    if _git(tree, "rev-parse", "--git-dir").returncode:
        return [f"{tree} is not a git repository: the ledger's history cannot be checked"]
    if _git(tree, "rev-parse", "--verify", "-q", "HEAD").returncode:
        return []                                       # a repository with no commit yet has no history to keep
    log = _git(tree, "log", "--format=%H", "--", rel)
    if log.returncode:
        return [f"git log failed in {tree}: {log.stderr.strip()[:200]}"]

    def show(rev: str) -> str | None:
        r = _git(tree, "show", f"{rev}:{rel}")
        return r.stdout if r.returncode == 0 else None

    head = show("HEAD") or ""
    problems = []
    for c in log.stdout.split():
        old = show(c)
        if old is None:
            continue                                    # the commit that deleted it: its parent is checked
        miss = missing_lines(old, head)
        if miss:
            problems.append(f"{c[:10]}: {len(miss)} committed line(s) of {rel} are not in HEAD (rewritten or removed), "
                            f"e.g. {miss[0][:160]}")
    work = tree / rel
    miss = missing_lines(head, work.read_text(encoding="utf-8") if work.is_file() else "")
    if miss:
        problems.append(f"the working copy of {rel} lost {len(miss)} line(s) committed at HEAD, e.g. {miss[0][:160]}")
    return problems


# --------------------------------------------------------------------------------------------------------- the reads


def _schema(path: Path) -> list[str]:
    import pyarrow.parquet as pq

    return list(pq.read_schema(path).names)


def _columns(path: Path, columns: Sequence[str] | None, what: str) -> list[str]:
    have = _schema(path)
    if columns is None:
        return have
    cols = list(columns)
    missing = [c for c in cols if c not in have]
    if missing:
        raise KeyError(f"{what}: {path.name} has no column(s) {missing} (it has {have})")
    return cols


def read_bars(start: Any, end: Any, *, purpose: str | None = None, declaration: Any = None,
              repeat: str | None = None, columns: Sequence[str] | None = None, market: str = "NQ",
              what: str = "bar read", design: Any = None, repo: Path | str | None = None):
    """Stage 2's 1-minute bars of `market` for trading days `start` to `end` (inclusive), after the seal and Stage 2's
    own window guard (the vendored `propedge.data.bars.read_bars`, purpose `development`). A judged-block read is
    ledgered before the bars are read. `columns` selects columns (all by default)."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    a = authorise(start, end, purpose=purpose, declaration=declaration, repeat=repeat, design=design, repo=tree,
                  what=what)
    if not NAME.fullmatch(market):
        raise ValueError(f"a market is a root such as 'NQ', not {market!r}")
    store = tree / STORE_REL
    path = store / market / "bars.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"{what}: no bar store at {path} (python scripts/vendor_stage2.py --data)")
    cols = _columns(path, columns, what)
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.data.bars import read_bars as vendored_read_bars
    from propedge.data.windows import assert_readable

    assert_readable(market, a.start, a.end, "development", what=what)     # Stage 2's guard first: no line if it refuses
    if a.ledgered:
        _record(a, "bars", [path], cols, what, tree)
    df = vendored_read_bars(market, a.start.isoformat(), a.end.isoformat(), "development", store=store, what=what)
    check_returned(df["day"].unique(), a.start, a.end)
    return df[cols] if columns is not None else df


def read_walks(family: str, table: str, start: Any, end: Any, *, purpose: str | None = None,
               declaration: Any = None, repeat: str | None = None, columns: Sequence[str] | None = None,
               market: str = "NQ", what: str = "walk read", design: Any = None, repo: Path | str | None = None):
    """A table of Stage 2's atlas walks (`vendor/stage2/data/atlas/<family>/<table>.parquet`, e.g. A3 `walks`, A1
    `events`/`days`/`walks`) for dates `start` to `end` (its `date` column), after the seal and Stage 2's own window
    guard (`propedge.data.windows.assert_readable`, purpose `development`). A judged-block read is ledgered before the
    table is read."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    a = authorise(start, end, purpose=purpose, declaration=declaration, repeat=repeat, design=design, repo=tree,
                  what=what)
    for x in (family, table, market):
        if not NAME.fullmatch(str(x)):
            raise ValueError(f"{what}: {x!r} is not a plain name (a family such as 'A3', a table such as 'walks')")
    path = tree / ATLAS_REL / family / f"{table}.parquet"
    if not path.is_file():
        raise FileNotFoundError(f"{what}: no walk table at {path} (python scripts/vendor_stage2.py --data)")
    cols = _columns(path, columns, what)
    if "date" not in _schema(path):
        raise KeyError(f"{what}: {path.name} has no `date` column, so its dates cannot be sealed")
    from extended import use_vendored_stage2

    use_vendored_stage2()
    from propedge.data.windows import assert_readable

    assert_readable(market, a.start, a.end, "development", what=what)
    if a.ledgered:
        _record(a, "walks", [path], cols, what, tree)
    import pandas as pd

    read = cols if "date" in cols else [*cols, "date"]
    df = pd.read_parquet(path, columns=read,
                         filters=[("date", ">=", a.start.isoformat()), ("date", "<=", a.end.isoformat())])
    check_returned(df["date"].astype(str).unique(), a.start, a.end)
    return df[cols].reset_index(drop=True)


def authorise_engine_read(start: Any, end: Any, *, files: Sequence[Path | str], what: str,
                          purpose: str | None = None, declaration: Any = None, repeat: str | None = None,
                          design: Any = None, repo: Path | str | None = None) -> Authorisation:
    """For a runner whose reads happen inside Stage 2's engine (the identities, the U1 replay, a cell rebuilt by
    `build_cells`): the same checks as a read here, and the same ledger line, for the `files` the engine will open.
    Reads no data; call it before the engine runs. A judged read names its files and they must exist, ledgered or
    not (an identity outside a clean run, E-026)."""
    tree = Path(repo).resolve() if repo is not None else ROOT
    a = authorise(start, end, purpose=purpose, declaration=declaration, repeat=repeat, design=design, repo=tree,
                  what=what)
    paths = [Path(f) if Path(f).is_absolute() else tree / f for f in files]
    if a.judged:
        if not paths:
            raise ValueError(f"{what}: a judged-block read names the files it opens")
        absent = [str(p) for p in paths if not p.is_file()]
        if absent:
            raise FileNotFoundError(f"{what}: {absent[:3]} do not exist")
    if a.ledgered:
        _record(a, "engine", paths, None, what, tree)
    return a


__all__ = ["CHOICE_START", "CHOICE_END", "JUDGED_START", "JUDGED_END", "CONFIRMATION_START", "SEAL_START", "IDENTITY",
           "LEDGER_REL", "Authorisation", "ReadRefused", "ConfirmationWindowRefused", "JudgedBlockSealed",
           "JudgedBlockReadTwice", "LedgerError", "span", "blocks_of", "check_returned", "declared_purposes", "pins",
           "REGISTERED_DESIGN", "REGISTERED_DESIGNS", "names_design",
           "decision_row", "authorise", "read_bars", "read_walks", "authorise_engine_read", "ledger_path",
           "read_ledger", "missing_lines", "ledger_history_problems"]
