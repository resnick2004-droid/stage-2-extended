"""RD-01's identity waits (R3 of the second read; D1 of E-104 and the third read's (a)) on the one shared parser,
`extended.identity_tokens` (Q-110): a runner that waits on identities starts only when each has a decision row
recording that it **held**, at code the run still runs.

**The token** is E-104's positional one, written in documents only as the placeholder identity-holds: <id>: the first
text of a row's third cell, `<stem>: <id> @ <sha> -- <text>`, unquoted; that shape anywhere else is never a token.
Its grammar, its breaches and its matching are `identity_tokens`' alone; nothing here parses a row.

**A wait** (`waited_problems`):
- refused outright unless `identity_tokens.problems` finds the log clean, before any wait is read;
- each wait is met by `identity_tokens.held(text, id, repo, head, covered)` -- the newest row carrying exactly that id
  whose positional sha is the commit being run or an ancestor of it with none of the covered paths changed since
  (only that sha is read; ids exact: Q-104 is neither Q-10 nor Q-104d) -- and when it is not, `held_report` gives
  every row's reason;
- the admitted row, its full sha and HEAD -- never the token string -- go in the run's manifests.

**RD-01's waits and their covers** (`waited`, `cover`; E-113, E-117, Q-111). The shared identities (Q-80, Q-93) cover
exactly `extended.identity_cover.cover(id)` -- never less; RD-01's own identity stage (Q-104) is declared here by the
same rule: `identity_cover.BASE` (the package root, the folder `config/` whole, both vendored manifests), its script
`identity/firms_identity.py`, and every repository file the shared import model (`identity_cover.imports`) finds it
reaching -- held to that rule by `identity_cover.uncovered` (`cover_problems`, refusing; an import the model cannot
resolve refuses too). A change under `config/` therefore fails every wait.

`covered` lists only real paths at HEAD (a folder covers everything under it); `held` refuses any other, and so does
the wait. `holding_cell` builds a holding's third cell for tests and for the lead, so no document types one.

Pure Python and git; nothing here imports the engine.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from extended import ROOT
from extended import identity_cover as IC
from extended import identity_tokens as IT

SHA = re.compile(r"[0-9a-f]{7,40}")


@dataclass(frozen=True)
class Waited:
    """One identity a runner waits on: its id (the shared grammar's), what it is, the paths it held on."""

    task: str
    what: str
    files: tuple[str, ...]

    def __post_init__(self) -> None:
        if not IT.ID.fullmatch(self.task):
            raise ValueError(f"a waited identity is named by a queue id or a lowercase label, got {self.task!r}")
        if not self.files:
            raise ValueError(f"{self.task}: an identity covers the files it held on; none given")


def holding_cell(ident: str, sha: str, text: str) -> str:
    """The third cell of a row recording that `ident` held at `sha` (E-104's positional form; `text` must say it
    holds, as the shared parser's breach (b) requires)."""
    if not IT.ID.fullmatch(str(ident)) or not SHA.fullmatch(str(sha)) or not str(text).strip():
        raise ValueError("a holding names an id, a 7- to 40-hex sha and its text")
    return f"{IT.STEM}: {ident} @ {sha} -- {text}"


def _full(repo: Path, rev: str) -> str | None:
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"], cwd=str(repo),
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def waited_problems(repo: Path | str, waited: Sequence[Waited], *, decisions_text: str | None = None,
                    head: str = "HEAD") -> tuple[list[str], dict[str, dict[str, str]]]:
    """(the problems, {id: the admitted row, its full sha, HEAD and what it is}) for every waited identity, each
    through `identity_tokens.held`; refused whole when the log has a breach. `decisions_text` defaults to the
    repository's `DECISIONS.md`; `head` is the commit being run."""
    repo = Path(repo)
    if decisions_text is None:
        p = repo / "DECISIONS.md"
        decisions_text = p.read_text(encoding="utf-8") if p.is_file() else ""
    breaches = IT.problems(decisions_text)
    if breaches:
        return [f"the decision log's identity tokens have {len(breaches)} breach(es), so no wait is read: "
                + "; ".join(breaches[:4])], {}
    head_full = _full(repo, head)
    if head_full is None:
        return [f"the commit being run ({head}) does not resolve"], {}
    problems: list[str] = []
    found: dict[str, dict[str, str]] = {}
    for w in waited:
        try:
            tok = IT.held(decisions_text, w.task, repo, head_full, list(w.files))
            why = [] if tok is not None else IT.held_report(decisions_text, w.task, repo, head_full, list(w.files))[1]
        except ValueError as exc:
            problems.append(f"{w.task} ({w.what}): refused by the shared parser -- {exc}")
            continue
        if tok is not None:
            found[w.task] = {"row": tok.row, "sha": _full(repo, tok.sha) or tok.sha, "head": head_full, "what": w.what}
        else:
            problems.append(f"{w.task} ({w.what}): " + "; ".join(why))
    return problems, found


#: RD-01's own identity stage
RD01_SCRIPT = "identity/firms_identity.py"
#: the identities RD-01 waits on, in order, with what each is
WHAT = {"Q-104": "RD-01's identity stage, identity/firms_identity.py (9.1 items 1-5, every start, 500 paths)",
        "Q-80": "Q-71's 500-path gate identities (A-8; P-14, P-16)",
        "Q-93": "Q-76's heavy identity with Q-100's (A-9: U1's start rows at the defaults and through the keywords)"}


def cover(ident: str) -> tuple[str, ...]:
    """The covered paths of a wait: a shared identity's by Q-111's declaration exactly; RD-01's own (Q-104) by the
    same rule, `BASE` and its script's closure under the shared import model."""
    if ident in IC.COVER:
        return IC.cover(ident)
    if ident == "Q-104":
        return tuple(dict.fromkeys(IC.BASE + IC.imports(RD01_SCRIPT, ROOT).files))
    raise ValueError(f"{ident!r} is no identity RD-01 waits on ({', '.join(WHAT)})")


def cover_problems() -> list[str]:
    """V4: why RD-01's own cover falls short of the rule (`identity_cover.uncovered`: a path missing, or an import the
    model cannot resolve -- a dynamic import among them); [] when it meets it."""
    return [f"Q-104's cover: {q}" for q in IC.uncovered(RD01_SCRIPT, cover("Q-104"), ROOT)]


def waited() -> tuple[Waited, ...]:
    """The identities RD-01 waits on (9.1, 15's waits), each with `cover`'s paths."""
    return tuple(Waited(i, WHAT[i], cover(i)) for i in WHAT)


__all__ = ["Waited", "holding_cell", "waited_problems", "RD01_SCRIPT", "WHAT", "cover", "cover_problems", "waited"]
