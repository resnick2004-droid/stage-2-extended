"""F-03 (family O): the runs' refusing guards and their sections (sections 9, 10, 12, 19; build item 18.1 item 5).

    from extended import opening_run as R
    pre = R.pre_run(ROOT, run=1)          # refuses (RunRefused) before anything is read
    pre.rows                              # the waited identities' decision rows, named in every manifest

**The guards, each refusing before anything is read** (A1; header; 19.2; E-052, E-094, E-095, E-098):

1. **the pass-line code's blobs** -- `git rev-parse HEAD:extended/lift_bound.py` is
   `984f3467a4a05aa790d3ea43e94ac7761f0725b2` and `HEAD:extended/p_bound.py` is
   `f5b29710e243f97a2795e57f6458512fea99199b`, and the working files are those blobs (A1 item 1);
2. **the level** -- the run's level is `lift_bound.family_level(12)` (k = 12, E-095), exactly;
3. **the judged session list** -- Q-83's `results/q82_judged_sessions.csv` (its manifest verified) holds 657 sessions
   whose ISO dates joined by LF hash to E-094's `d1e4524b...` (7.2; E-052 (3)'s assertions carried);
4. **the declaration** -- `prereg/F-03_opening_timing.md` hashes (LF) to E-095's pin, a DECISIONS row carries that pin,
   and its `Judged-block reads:` line names exactly the four purposes (19.1);
5. **the waited identities by E-104's positional token** (E-098 as amended) -- for each of Q-89 (Q-70's place
   records), Q-93 (Q-76's class on the U1 replay), Q-101 (Q-94's replay recorder), Q-80 (the gate's 500-path
   identities) and A0's own (`A0_ID`), by the one parser, `extended.identity_tokens` (Q-110): the decision log has no
   breach of the token rule (`IT.problems`, else nothing is read), and for each wait a row whose token for its id is at
   a commit that is HEAD or an ancestor of it, with none of its covered files (`WAITS`: the code it certifies) changed
   since (`IT.held_report`); the rows are named in every manifest (`PreRun.rows`);
6. **a clean run** for anything that writes a result (`extended.results.clean_run_problem`).

**What run 1 and run 2 read** (19.1, 19.2): run 1 the choice block only, no tag; run 2 the judged block under the four
purposes in stage C's order (`PURPOSES`), each through `extended/reader.py` from the clean run, once (`repeat=` only
under a row naming the declaration, passed through). The judge's entry point reads the pick and u3's frozen forecast
by their pinned hashes (T-9): run 1's result file's sha256 and the forecast's sha256 must both appear in one decision
row naming F-03 (`pinned_run1_problems`).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from extended import lift_bound as LB

FAMILY = "F-03"
DECLARATION = "prereg/F-03_opening_timing.md"
DECLARATION_SHA256 = "fc64ae3cccf648ff5bf90f8cc7772ebb351c78763064ec0f856edb789860898a"
PIN_ROW = "E-095"
K = 12
LEVEL = LB.family_level(K)
#: the judged block's purposes in stage C's order (19.1)
PURPOSES = ("stage_C_states", "stage_C_judgement", "stage_C_campaign", "stage_C_scorecard")
#: the pass-line code, pinned by git blob id (E-052; the header's withdrawal clause)
PINNED_BLOBS = {"extended/lift_bound.py": "984f3467a4a05aa790d3ea43e94ac7761f0725b2",
                "extended/p_bound.py": "f5b29710e243f97a2795e57f6458512fea99199b"}
#: the infrastructure identities waited for (header; 20 item 4), and A0's own (20 item 6), each with the files it certifies
#: (E-104: a waited identity counts only where none of its covered files changed since the commit it held at)
WAITED = ("Q-89", "Q-93", "Q-101", "Q-80")
#: A0's id in its token -- a lowercase label (E-104's grammar `[a-z][a-z0-9_]*`); the lead may number A0's run otherwise, and then this
#: constant is changed in a code commit before run 1 (said in the build's hand-back)
A0_ID = "f03_a0"
A0_QUEUE_ID = A0_ID
#: each waited identity's script; its covered paths are `cover(ident)` (E-113's rule; Q-111's `identity_cover` will
#: replace the shared ones)
SCRIPTS: dict[str, str] = {"Q-89": "identity/place_records_identity.py", "Q-93": "identity/user_beside_identity.py",
                           "Q-101": "identity/replay_records_identity.py", "Q-80": "identity/gate_identity.py",
                           A0_ID: "identity/family_o_identity.py"}
COVER_BASE = ("extended/__init__.py", "vendor/MANIFEST_stage2.sha256", "vendor/DATA_MANIFEST_stage2.sha256")


def _module_file(root: Path, name: str, here: Path) -> Path | None:
    """A repository module's file for an import name (`extended.x`, `x` beside the importer, a script), or None."""
    parts = name.split(".")
    for base in (root, here.parent, root / "identity", root / "scripts"):
        f = base.joinpath(*parts).with_suffix(".py")
        if f.is_file() and "vendor" not in f.relative_to(root).parts:
            return f
        d = base.joinpath(*parts) / "__init__.py"
        if d.is_file() and "vendor" not in d.relative_to(root).parts:
            return d
    return None


def imports_of(root: Path, rel: str) -> set[str]:
    """Every repository module `rel` imports, directly or not (any import statement, top-level or inside a function),
    as repository-relative paths; vendored modules are covered by the vendored manifest."""
    import ast

    root = Path(root)
    seen: set[str] = set()
    todo = [root / rel]
    while todo:
        f = todo.pop()
        r = f.relative_to(root).as_posix()
        if r in seen:
            continue
        seen.add(r)
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
            for n in names:
                m = _module_file(root, n, f)
                if m is not None and m.relative_to(root).as_posix() not in seen:
                    todo.append(m)
    return seen


def cover(ident: str, root: Path | None = None) -> tuple[str, ...]:
    """A waited identity's covered paths (E-113): the base (`extended/__init__.py`, both vendored manifests), the
    identity's own script, and every repository module that script imports, directly or not."""
    from extended import ROOT as _ROOT

    r = Path(root) if root is not None else _ROOT
    return tuple(sorted(set(COVER_BASE) | imports_of(r, SCRIPTS[ident])))


WAITS: dict[str, tuple[str, ...]] = {ident: () for ident in SCRIPTS}       # filled by `waits()`


def waits(root: Path | None = None) -> dict[str, tuple[str, ...]]:
    """{id: its covered paths} for every waited identity, by `cover`."""
    return {ident: cover(ident, root) for ident in SCRIPTS}


ROW = re.compile(r"^\|\s*(E-\d+)\s*\|")
#: the cells (4, s3 dropped at the pin and counted, E-095), the searched configurations and the fitted values (17)
CELL_COUNTS = {"cells": 4, "dropped_at_pin": ["s3"], "searched": 0, "fitted_values": 11}
RESULT = "fo_opening"
JOURNEY = "fo_journey"
SECTIONS = ("identity", "states", "persistence", "supply", "openings", "resolution", "wait", "power", "level_control",
            "choice", "level", "judged", "campaign", "floor", "beside")
RUN1_SECTIONS = SECTIONS[:10]


class RunRefused(RuntimeError):
    """A guard refused: nothing is read or written."""


# ------------------------------------------------------------------------------------------------ git blobs


def blob_id(path: Path) -> str:
    """git's blob id of a file's bytes as committed (`git hash-object`: LF bytes as stored)."""
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def head_blob(repo: Path, rel: str) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "rev-parse", f"HEAD:{rel}"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def blob_problems(repo: Path, pinned: Mapping[str, str] = PINNED_BLOBS) -> list[str]:
    """A1 item 1: HEAD's blobs of the two pass-line modules are the pinned ones, and the working files are HEAD's
    (`git hash-object`, which applies the checkout's filters)."""
    out = []
    for rel, want in pinned.items():
        got = head_blob(repo, rel)
        if got != want:
            out.append(f"HEAD:{rel} is blob {got}, not the pinned {want} (E-052; a changed module is a new family)")
            continue
        r = subprocess.run(["git", "-C", str(repo), "hash-object", rel], capture_output=True, text=True)
        if r.returncode != 0 or r.stdout.strip() != want:
            out.append(f"the working {rel} is not HEAD's pinned blob {want[:12]}")
    return out


# ------------------------------------------------------------------------------------------------ the decision log


#: each admitted wait's commit, from its row's token (the manifest names it, E-106's rule)
COMMITS: dict[str, str] = {}


def waited_problems(decisions_text: str, waits: Mapping[str, Sequence[str]], repo: Path, head: str = "HEAD"
                    ) -> tuple[list[str], dict[str, list[str]]]:
    """(why the waits are not met, {id: the row that counts}) by the one parser (`extended.identity_tokens`, Q-110;
    E-104): first `IT.problems(text)` must be empty -- any breach refuses before a wait is read; then each waited
    identity by `IT.held_report(text, ident, repo, head, covered)` (refused there too: an id outside the grammar, a
    covered path not in `head`)."""
    from extended import identity_tokens as IT

    breaches = IT.problems(decisions_text)
    if breaches:
        return [f"DECISIONS.md breaches the token rule (E-104), so no wait is read: {b_}" for b_ in breaches], {}
    bad: list[str] = []
    rows: dict[str, list[str]] = {}
    COMMITS.clear()
    for ident, covered in waits.items():
        try:
            tok, why = IT.held_report(decisions_text, ident, repo, head, list(covered))
        except ValueError as exc:
            bad.append(f"{ident}: {exc}")
            rows[ident] = []
            continue
        rows[ident] = [tok.row] if tok is not None else []
        if tok is not None:
            COMMITS[ident] = tok.sha
        if tok is None:
            bad.append(f"{ident} is not on record as holding at {head} for its covered files: " + "; ".join(why))
    return bad, rows


def declaration_problems(repo: Path, decisions_text: str) -> list[str]:
    """The pinned text unchanged, pinned, and naming exactly the four purposes."""
    from extended import reader

    p = Path(repo) / DECLARATION
    if not p.is_file():
        return [f"{DECLARATION} does not exist"]
    out = []
    sha = reader.sha256_lf(p)
    if sha != DECLARATION_SHA256:
        out.append(f"{DECLARATION} hashes to {sha[:12]}, not E-095's pin {DECLARATION_SHA256[:12]}: the text changed")
    if DECLARATION_SHA256 not in reader.pins(decisions_text).get(DECLARATION, set()):
        out.append(f"no decision row pins {DECLARATION} at {DECLARATION_SHA256[:12]}")
    got = reader.declared_purposes(p.read_text(encoding="utf-8"))
    if got != frozenset(PURPOSES):
        out.append(f"the text's judged-block reads are {sorted(got)}, not {list(PURPOSES)}")
    return out


def level_problems(level: float, k: int = K) -> list[str]:
    want = LB.family_level(int(k))
    return [] if float(level) == want and int(k) == K else [f"the level {level!r} at k = {k} is not family_level({K}) "
                                                            f"= {want!r} (E-095)"]


def session_list_problems(results_dir: Path) -> tuple[list[str], list[str]]:
    """(problems, the judged session list): Q-83's file, 657 sessions, E-094's sha256."""
    from extended import opening_population as OP

    try:
        cal, _ = OP.read_judged_sessions(results_dir)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        return [str(exc)], []
    return [], cal


@dataclass
class PreRun:
    rows: dict[str, list[str]]
    judged_sessions: list[str]
    problems: list[str] = field(default_factory=list)
    commits: dict[str, str] = field(default_factory=dict)

    def parameters(self) -> dict[str, Any]:
        return {"identity_rows": self.rows, "identity_token_rule": "E-104 by extended.identity_tokens (Q-110)",
                "identity_covered": {k: list(v) for k, v in waits().items()}, "declaration": DECLARATION,
                "declaration_sha256": DECLARATION_SHA256, "pin_row": PIN_ROW, "k": K, "level": LEVEL,
                "pinned_blobs": dict(PINNED_BLOBS), "judged_sessions": len(self.judged_sessions),
                "judged_sessions_sha256": hashlib.sha256("\n".join(self.judged_sessions).encode()).hexdigest()
                if self.judged_sessions else None, **CELL_COUNTS}


def pre_run(repo: Path, *, results_dir: Path | None = None, level: float = LEVEL, need_clean: bool = True,
            waits: Mapping[str, Sequence[str]] | None = None, decisions_text: str | None = None,
            head: str = "HEAD") -> PreRun:
    """Every guard of the module docstring; `RunRefused` with every failure, before anything is read."""
    repo = Path(repo)
    text = decisions_text if decisions_text is not None else (repo / "DECISIONS.md").read_text(encoding="utf-8")
    problems = list(blob_problems(repo)) + level_problems(level) + declaration_problems(repo, text)
    bad, rows = waited_problems(text, globals()["waits"](repo) if waits is None else waits, repo, head)
    problems += bad
    sp, cal = session_list_problems(Path(results_dir) if results_dir is not None else repo / "results")
    problems += sp
    if need_clean:
        from extended.results import clean_run_problem

        c = clean_run_problem()
        if c:
            problems.append(c)
    pre = PreRun(rows, cal, problems, dict(COMMITS))
    if problems:
        raise RunRefused("REFUSED (F-03): " + "; ".join(problems))
    return pre


def pinned_run1_problems(decisions_text: str, run1_sha256: str, forecast_sha256: str | None,
                         fold_sha256s: Sequence[str] = ()) -> list[str]:
    """T-9: run 2 reads the pick and u3's forecast only by hashes the lead pinned -- one decision row naming F-03 that
    carries run 1's result file's sha256 and (when u3 is the pick or its forecast is read) the forecast's."""
    for line in decisions_text.splitlines():
        if ROW.match(line) and FAMILY in line and run1_sha256 in line and (forecast_sha256 is None
                                                                          or forecast_sha256 in line) \
                and all(f in line for f in fold_sha256s):
            return []
    return [f"no decision row naming {FAMILY} pins run 1's result ({run1_sha256[:12]})"
            + (f" and u3's forecast ({forecast_sha256[:12]})" if forecast_sha256 else "")
            + (f" and its {len(fold_sha256s)} fold fits" if fold_sha256s else "")
            + " (19.2: the lead's row between the two runs)"]


def file_sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------------ the sections


def rows(section: str, records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [{"section": section, **{k: _plain(v) for k, v in r.items()}} for r in records]


def _plain(v: Any) -> Any:
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (list, tuple, dict)):
        return json.dumps(v, sort_keys=True, default=str)
    return v


def frame(records: Sequence[Mapping[str, Any]], allowed: Sequence[str]) -> pd.DataFrame:
    """The result frame; refused (`RunRefused`) when a row's section is not one the run writes."""
    bad = sorted({str(r.get("section")) for r in records} - set(allowed))
    if bad:
        raise RunRefused(f"REFUSED (F-03): sections {bad} are not this run's ({list(allowed)})")
    return pd.DataFrame(list(records))


def choice_pick(choice: pd.DataFrame) -> dict[str, Any]:
    """T-14: the pick read back from a written `choice` section alone -- the row `kind == 'pick'`."""
    p = choice[(choice["section"] == "choice") & (choice["kind"] == "pick")]
    if len(p) != 1:
        raise RunRefused(f"REFUSED (F-03): the choice section holds {len(p)} pick rows")
    r = p.iloc[0]
    return {"pick": None if pd.isna(r.get("cell")) or r.get("cell") in ("", "none") else str(r["cell"]),
            "killed": bool(r.get("killed"))}


__all__ = ["FAMILY", "DECLARATION", "DECLARATION_SHA256", "PIN_ROW", "K", "LEVEL", "PURPOSES", "PINNED_BLOBS", "WAITED",
           "A0_ID", "A0_QUEUE_ID", "WAITS", "SCRIPTS", "COVER_BASE", "imports_of", "cover", "waits", "CELL_COUNTS", "RESULT", "JOURNEY", "SECTIONS", "RUN1_SECTIONS",
           "RunRefused", "blob_id", "head_blob", "blob_problems", "waited_problems", "declaration_problems",
           "level_problems", "session_list_problems", "PreRun", "pre_run", "pinned_run1_problems", "file_sha256",
           "rows", "frame", "choice_pick"]
