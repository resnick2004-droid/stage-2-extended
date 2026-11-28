"""The Mac run agent's assignment file (Q-229, E-298 (4)): its schema and its refusals.

    from extended import mac_assignments as MA
    book = MA.parse(text)          # raises MA.AssignmentError listing every problem; nothing partial is returned
    MA.expected_files(book.runs[0])  # the outputs and their sidecar manifests

The file is `config/mac_assignments.json`, committed, **edited by the lead only** on master; the agent
(`scripts/mac_agent.py`) reads it from `origin/master`, never from a local copy, and the lead's collect step
(`scripts/mac_collect.py`) reads it from there too. Its form:

    {"version": 1, "about": "...", "runs": [<run>, ...], "failures_acknowledged": ["<run name>", ...]}

Each run has exactly the fields `FIELDS` (and an optional `note`):

- `name`     the run's name: the clean checkout's folder, its log, and the branch `mac/<name>` (`NAME`: lower-case
             letters and digits in words joined by `-` or `_`, at most 64 characters); unique in the file;
- `commit`   the full 40-character sha the run is made from (a short sha is refused);
- `command`  the exact command, starting `python scripts/` or `python identity/` (`COMMAND`); only the characters of
             `SAFE` (no shell syntax, no quoting: it is split on spaces and run without a shell); never one of the
             agent's own scripts (`FORBIDDEN_SCRIPTS`);
- `hours`    the expected duration, a number in (0, `MAX_HOURS`];
- `mem_gb`   the memory the run needs, a number in (0, `MAX_MEM_GB`];
- `task`     the TASK_QUEUE id (`TASK`, e.g. `Q-188b`);
- `outputs`  the result files the run writes, each `results/<file>.csv` (`OUTPUT`), at least one, none twice; each
             one's sidecar manifest is expected beside it.

`failures_acknowledged` lists run names whose failure the lead has seen: the agent never re-runs a failed assignment,
and while a failure is not acknowledged it starts nothing new.

**The held-out and confirmation-window markers** (`window_markers`): every text field (name, command, task, outputs,
note) is refused when it holds a date (`2024-01-02`, `2024/01/02`, `20240102`, `2024_01_02`) on or after the seal's
first day (`extended.reader.SEAL_START`: every day after the choice block, the judged block and the confirmation
window from `extended.reader.CONFIRMATION_START` included); a word marking the held-out block or the confirmation
window (`MARKER_WORDS`: held-out / holdout / judged / confirm... / verdict / oos); an option naming a block
(`--block`, `--journey-block`, ...) with any value but `search` or `choice`; or a year from 2024 on given to an option
about years, dates or days. What it cannot see (said, not hidden): a held-out read a script makes by its own default;
the reader's seal (`extended.reader`) is the guard for that, inside the run.

Light: the standard library and `extended.reader`'s constants (which import no engine).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from extended.reader import CONFIRMATION_START, SEAL_START

CONFIG_REL = "config/mac_assignments.json"
VERSION = 1
FIELDS = ("name", "commit", "command", "hours", "mem_gb", "task", "outputs")
OPTIONAL = ("note",)
TOP = ("version", "about", "runs", "failures_acknowledged")
MANIFEST_SUFFIX = ".manifest.json"          # the vendored writer's (propedge.reporting.results.MANIFEST_SUFFIX)

NAME = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
NAME_MAX = 64
SHA = re.compile(r"[0-9a-f]{40}")
TASK = re.compile(r"Q-\d+[a-z]?")
OUTPUT = re.compile(r"results/[A-Za-z0-9][A-Za-z0-9_.-]*\.csv")
COMMAND = re.compile(r"python (?:scripts|identity)/[A-Za-z0-9_][A-Za-z0-9_/-]*\.py(?: .*)?")
SAFE = re.compile(r"[A-Za-z0-9 _./:,=+-]+")
FORBIDDEN_SCRIPTS = ("scripts/mac_agent.py", "scripts/mac_collect.py", "scripts/run_clean.py", "scripts/run_lock.py",
                     "scripts/worktrees.py", "scripts/install_hooks.py")
MAX_HOURS = 24.0
MAX_MEM_GB = 64.0

#: words marking the held-out block or the confirmation window
MARKER_WORDS = re.compile(r"held[-_ ]?out|hold[-_ ]?out|judged|confirm|verdict|(?<![a-z])oos(?![a-z])", re.IGNORECASE)
#: a date in any of the forms a command or a file name could carry
DATE = re.compile(r"(?<!\d)((?:19|20)\d{2})([-_/.]?)(\d{2})\2(\d{2})(?!\d)")
#: option-name words whose value is a year, a date or a day
DATE_OPTION_WORDS = frozenset({"year", "years", "date", "dates", "day", "days", "from", "to", "until", "since",
                               "end", "window", "through", "upto"})
BLOCK_OK = frozenset({"search", "choice"})
YEAR = re.compile(r"\d{4}")


class AssignmentError(ValueError):
    """The assignment file is refused; `problems` lists every reason."""

    def __init__(self, problems: list[str]):
        self.problems = list(problems)
        super().__init__("the assignment file is refused:\n  - " + "\n  - ".join(self.problems))


@dataclass(frozen=True)
class Run:
    name: str
    commit: str
    command: str
    hours: float
    mem_gb: float
    task: str
    outputs: tuple[str, ...]
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        d = {"name": self.name, "commit": self.commit, "command": self.command, "hours": self.hours,
             "mem_gb": self.mem_gb, "task": self.task, "outputs": list(self.outputs)}
        if self.note:
            d["note"] = self.note
        return d

    def argv(self) -> list[str]:
        """The command's words (it holds no quoting: `SAFE`), "python" first."""
        return self.command.split()


@dataclass(frozen=True)
class Book:
    runs: tuple[Run, ...]
    failures_acknowledged: frozenset[str] = field(default_factory=frozenset)

    def by_name(self, name: str) -> Run | None:
        return next((r for r in self.runs if r.name == name), None)


def _is_date(y: str, m: str, d: str) -> date | None:
    try:
        return date(int(y), int(m), int(d))
    except ValueError:
        return None


def window_markers(text: str) -> list[str]:
    """Every held-out or confirmation-window marker found in `text` (empty: none found)."""
    found: list[str] = []
    for m in DATE.finditer(text):
        day = _is_date(m.group(1), m.group(3), m.group(4))
        if day is not None and day >= SEAL_START:
            where = "the confirmation window" if day >= CONFIRMATION_START else "the held-out years"
            found.append(f"the date {m.group(0)} is in {where} (from {SEAL_START.isoformat()} on)")
    for m in MARKER_WORDS.finditer(text):
        found.append(f"the word {m.group(0)!r} marks the held-out block or the confirmation window")
    words = text.split()
    for i, w in enumerate(words):
        if not w.startswith("--"):
            continue
        opt, eq, val = w[2:].partition("=")
        if not eq:
            val = words[i + 1] if i + 1 < len(words) else ""
        parts = set(re.split(r"[-_]", opt.lower()))
        if "block" in parts and val.lower() not in BLOCK_OK:
            found.append(f"the option --{opt} names the block {val!r} (only {sorted(BLOCK_OK)})")
        if parts & DATE_OPTION_WORDS and YEAR.fullmatch(val) and int(val) > SEAL_START.year:
            found.append(f"the option --{opt} gives the year {val} (the held-out years start {SEAL_START.year + 1})")
    return found


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v


def check_run(r: Any, i: int) -> list[str]:
    """Every problem of one run entry (`i` its place in the list, for the messages)."""
    if not isinstance(r, dict):
        return [f"runs[{i}] is not an object"]
    who = f"runs[{i}] ({r.get('name')!r})"
    bad: list[str] = []
    for k in FIELDS:
        if k not in r:
            bad.append(f"{who}: the field {k!r} is missing")
    for k in r:
        if k not in FIELDS and k not in OPTIONAL:
            bad.append(f"{who}: the field {k!r} is not in the schema ({', '.join(FIELDS + OPTIONAL)})")
    name = r.get("name")
    if "name" in r and not (isinstance(name, str) and NAME.fullmatch(name) and len(name) <= NAME_MAX):
        bad.append(f"{who}: the name must be lower-case words joined by - or _ (at most {NAME_MAX} characters)")
    c = r.get("commit")
    if "commit" in r and not (isinstance(c, str) and SHA.fullmatch(c)):
        bad.append(f"{who}: the commit must be a full 40-character lower-case sha (a short sha is refused)")
    cmd = r.get("command")
    if "command" in r:
        unsafe = not isinstance(cmd, str) or not SAFE.fullmatch(cmd) or "  " in cmd or cmd != cmd.strip()
        if unsafe:
            bad.append(f"{who}: the command holds characters outside {SAFE.pattern} (no shell syntax, no quoting) or "
                       "doubled or outer spaces")
        if not isinstance(cmd, str) or not COMMAND.fullmatch(cmd):
            bad.append(f"{who}: the command must start 'python scripts/' or 'python identity/' and name a .py script")
        elif not unsafe:
            script = cmd.split()[1]
            if ".." in script.split("/"):
                bad.append(f"{who}: the script path climbs out of its folder")
            if script in FORBIDDEN_SCRIPTS:
                bad.append(f"{who}: the command runs {script}, one of the agent's own scripts")
    for k, hi in (("hours", MAX_HOURS), ("mem_gb", MAX_MEM_GB)):
        if k in r and not (_num(r[k]) and 0 < r[k] <= hi):
            bad.append(f"{who}: {k} must be a number in (0, {hi}]")
    t = r.get("task")
    if "task" in r and not (isinstance(t, str) and TASK.fullmatch(t)):
        bad.append(f"{who}: the task must be a TASK_QUEUE id such as Q-188b")
    outs = r.get("outputs")
    if "outputs" in r:
        if not isinstance(outs, list) or not outs:
            bad.append(f"{who}: outputs must be a non-empty list")
        else:
            for o in outs:
                if not (isinstance(o, str) and OUTPUT.fullmatch(o)) or str(o).endswith(MANIFEST_SUFFIX):
                    bad.append(f"{who}: the output {o!r} is not results/<file>.csv")
            if len(set(map(str, outs))) != len(outs):
                bad.append(f"{who}: an output is listed twice")
    note = r.get("note", "")
    if not isinstance(note, str):
        bad.append(f"{who}: the note must be text")
    texts = [v for v in (name, cmd, t, note) if isinstance(v, str)]
    texts += [o for o in (outs if isinstance(outs, list) else []) if isinstance(o, str)]
    for s in texts:
        for why in window_markers(s):
            bad.append(f"{who}: {why}")
    return bad


def check(doc: Any) -> list[str]:
    """Every problem of a parsed assignment file; empty when it is accepted."""
    if not isinstance(doc, dict):
        return ["the file is not a JSON object"]
    bad: list[str] = []
    for k in doc:
        if k not in TOP:
            bad.append(f"the top-level field {k!r} is not in the schema ({', '.join(TOP)})")
    if doc.get("version") != VERSION:
        bad.append(f"version must be {VERSION}")
    runs = doc.get("runs")
    if not isinstance(runs, list):
        bad.append("runs must be a list")
        runs = []
    for i, r in enumerate(runs):
        bad.extend(check_run(r, i))
    names = [r.get("name") for r in runs if isinstance(r, dict)]
    for n in sorted({n for n in names if isinstance(n, str) and names.count(n) > 1}):
        bad.append(f"the run name {n!r} appears more than once")
    acks = doc.get("failures_acknowledged", [])
    if not isinstance(acks, list) or not all(isinstance(a, str) and NAME.fullmatch(a) for a in acks):
        bad.append("failures_acknowledged must be a list of run names")
    return bad


def _no_dupes(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise AssignmentError([f"the key {k!r} appears twice in one object"])
        out[k] = v
    return out


def _no_constant(c: str) -> Any:
    raise AssignmentError([f"the constant {c} is not JSON"])


def parse(text: str) -> Book:
    """The accepted assignment file, or AssignmentError with every problem."""
    try:
        doc = json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_no_constant)
    except json.JSONDecodeError as exc:
        raise AssignmentError([f"not JSON: {exc}"]) from None
    bad = check(doc)
    if bad:
        raise AssignmentError(bad)
    runs = tuple(Run(name=r["name"], commit=r["commit"], command=r["command"], hours=float(r["hours"]),
                     mem_gb=float(r["mem_gb"]), task=r["task"], outputs=tuple(r["outputs"]), note=r.get("note", ""))
                 for r in doc["runs"])
    return Book(runs=runs, failures_acknowledged=frozenset(doc.get("failures_acknowledged", [])))


def expected_files(run: Run) -> set[str]:
    """The files a run's checkout must hold changed after it, exactly: each output and its sidecar manifest."""
    return {p for o in run.outputs for p in (o, o + MANIFEST_SUFFIX)}


#: the identity fields of a run: what the record on a `mac/<run>` branch must repeat for the collect to accept it
IDENTITY_FIELDS = ("name", "commit", "command", "task", "outputs")


def same_identity(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return all(a.get(k) == b.get(k) for k in IDENTITY_FIELDS)


__all__ = ["CONFIG_REL", "FIELDS", "AssignmentError", "Run", "Book", "parse", "check", "check_run",
           "window_markers", "expected_files", "same_identity", "IDENTITY_FIELDS", "MANIFEST_SUFFIX"]
