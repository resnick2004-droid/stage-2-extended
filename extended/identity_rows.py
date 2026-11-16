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


def import_closure(script: str, repo: Path | str) -> tuple[str, ...]:
    """E-113's rule for what an identity covers beyond its base: every repository module `script` imports, directly
    or not -- each `import` and `from ... import` anywhere in a file (a function's own included), resolved to this
    repository's files: `extended` and its modules (`from extended import x` names `extended/x.py` where it is a
    module), and a bare name to a file of the importing file's own folder (an identity script's `identity/`, as it puts
    that folder on its path). Vendored and third-party names resolve to nothing here (the vendored code is the
    manifest's). The script itself is not in the answer; repository-relative paths, sorted."""
    import ast

    repo = Path(repo)

    def resolve(mod: str, names: list[str], here: Path) -> list[Path]:
        parts = mod.split(".") if mod else []
        out: list[Path] = []
        if parts and parts[0] == "extended":
            pkg = repo.joinpath(*parts)
            for cand in (pkg.with_suffix(".py"), pkg / "__init__.py"):
                if cand.is_file():
                    out.append(cand)
            out.append(repo / "extended" / "__init__.py")
            if pkg.is_dir():
                out += [pkg / f"{n}.py" for n in names if (pkg / f"{n}.py").is_file()]
        elif len(parts) == 1 and (here / f"{parts[0]}.py").is_file():
            out.append(here / f"{parts[0]}.py")
        return out

    seen: set[Path] = set()
    todo = [repo / script]
    while todo:
        f = todo.pop()
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                hits = [x for a in node.names for x in resolve(a.name, [], f.parent)]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = f.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    mod = ".".join(base.relative_to(repo).parts + ((node.module,) if node.module else ()))
                else:
                    mod = node.module or ""
                hits = resolve(mod, [a.name for a in node.names], f.parent)
            else:
                continue
            for h in hits:
                h = h.resolve()
                if h not in seen and h != (repo / script).resolve():
                    seen.add(h)
                    todo.append(h)
    return tuple(sorted(x.relative_to(repo.resolve()).as_posix() for x in seen))


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


__all__ = ["Waited", "holding_cell", "import_closure", "waited_problems"]
