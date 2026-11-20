"""The search years' cut at the read (Q-172; the lead's option 2; the O-7 red team's B-2 and m-3,
`docs/reviews/O7_SEARCH_YEARS_2026-11-19.md`): Stage 2's builders run unedited on NQ's search years only, every row
after the cut's last day (2023-12-29 by default, E-208) dropped **as it is read**, so no held-out outcome can enter a
job, a bound, a capacity or a mark built inside the cut.

    from extended import use_vendored_stage2; use_vendored_stage2()
    from extended import search_cut as SC
    SC.authorise(purpose="...", declaration="E-NNN", what="...")    # extended.reader's door for the engine's read
    with SC.cut() as log:                                             # every data read below is cut or refused
        jobs, c, bad = user_beside_identity.build(rd, "p14")         # the vendored builder, unedited
    log.problems()                                                    # [] when every read was a wrapped one

**Why at the read.** The builders open their inputs whole: A1's events and days through `pd.read_parquet` in
`a3_resolution_map.load_a1`, A3's walk through `pd.read_parquet` in `atlas_a3.cached_walk` (both under
`atlas_a3.load_inputs`), and the bars through `propedge.data.bars.read_bars` (P-16's walk, `atlas_a3.bar_arrays`),
which also calls `pd.read_parquet`. Cutting a job afterwards leaves every whole-window statistic the builder computed on
the way in it (a pooled bound, a busiest day, a resolved mark). Cutting the rows as they are read leaves none.

**The inputs and the cut for each** (`WRAPPED`, paths under the vendored tree; the only files the cut lets a builder
read as data):

| file | key column | the cut |
|---|---|---|
| `data/atlas/A1/events.parquet` | `date` | rows with `date` <= the last day (a pyarrow filter at the read, then checked) |
| `data/atlas/A1/days.parquet` | `date` | the same |
| `data/atlas/A1/walks.parquet` | `date` | the same |
| `data/atlas/A3/walks.parquet` | `date` | the same |
| `data/bars/<ROOT>/bars.parquet` | `day` | the same, on the trading day |

**Read whole, never cut** (`PASSTHROUGH`): every `manifest.json` under `data/bars/` and `data/atlas/` -- metadata, no
price. In particular **the bars manifest's `day_list` is never cut**: `a3_resolution_map.load_a1` refuses unless the
A1 cache's manifest names the day count and last day of the bars manifest's `day_list`, so a cut list would refuse the
build. The day set the builders use is A1's `days` table, which is cut; `day_list` decides nothing else in these builds.

**Refused** (`UnwrappedRead`, raised inside the builder before anything is read): any parquet read anywhere that is not
a `WRAPPED` file; any other file opened under `data/bars/` or `data/atlas/` (Python's `open`, `io.open`, so pandas'
CSV readers and `Path.read_text` too); a wrapped file whose key column is missing; and any row past the last day that
the filter let through (checked on every frame read). A read made while the cut is active is recorded in its `CutLog`
(the file, the rows kept, the last key kept); the log is what a caller checks (`problems`, `files_read`).

**Vendored checks switched off: none.** No vendored function is replaced and no vendored check is suppressed: P-14's
build (`customer_journey.Inputs` for the `p13` kind, `customer_slices.p13_campaign`, `a3_compliance.campaign_inputs`)
runs every check it has on the cut rows. A build that needs a check switched off (the O-7 red team's m-3 names
`rc_dev_test.trade_problems` and P-15's content hash for the P-15 and P-16 builds) adds it to `SWITCHED_OFF` here,
under its own decision row, with the reason -- nothing else may be switched off, and `switched_off()` is what a
manifest prints. `SWITCHED_OFF` is empty at this commit.

**What the cut does to a build, stated for its readers** (RD-06 to RD-10, the cut G-3 and B-2): every statistic a
builder computes from rows is the search years' own -- P-14's pooled bounds and eras (era 2 of P-11's spans is 2023
alone on the default cut, its bootstrap degenerate; the O-7 red team's M-1), the busiest day's capacity, P-16's
resolved marks. A build from a configuration or a result file (the rung rule, the `noclose` policy table, FV3-C's
config) is not cut: those were chosen on the whole window, and the held-out ledger carries them (CHARTER 3.6 (b)).
The runner's own refusal of any block or date after the last day stays the backstop (`check_dates`): the builders
make a block for every day of A1's `days` table, so a read that escaped the cut would show as a late day.

**The reader's door.** The engine opens the files itself, so `authorise` calls `extended.reader.authorise_engine_read`
for the cut's span (from 2020-01-02 to the last day) with the files it wraps, before the build, and refuses an
authorisation that reaches the judged block. A choice-block read is not ledgered (E-019).

This module imports no engine at import time; `cut()` patches `pandas.read_parquet`, `builtins.open` and `io.open`
for its duration in this process only (a pool's workers are not covered: build inside the cut, run the pool after).
"""
from __future__ import annotations

import builtins
import contextlib
import fnmatch
import io
import os
import threading
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator, Sequence

from extended import VENDOR_STAGE2
from extended import reader as R

TASK = "Q-172"
#: the default cut: the search years' last day (E-208)
LAST_DAY = R.CHOICE_END
FIRST_DAY = R.CHOICE_START
#: the files a builder may read as data under the cut, relative to the vendored tree, and the key column cut on
WRAPPED: dict[str, str] = {
    "data/atlas/A1/events.parquet": "date",
    "data/atlas/A1/days.parquet": "date",
    "data/atlas/A1/walks.parquet": "date",
    "data/atlas/A3/walks.parquet": "date",
    "data/bars/*/bars.parquet": "day",
}
#: read whole, never cut: metadata only (the bars manifest's `day_list` among them)
PASSTHROUGH = ("data/bars/*/manifest.json", "data/atlas/*/manifest.json")
#: the guarded data folders: any other file opened under these is refused
GUARDED = ("data/bars", "data/atlas")
#: vendored checks switched off under the cut, each `name: reason (row)`; none at this commit
SWITCHED_OFF: dict[str, str] = {}


class UnwrappedRead(RuntimeError):
    """A builder read a data file the cut does not wrap, or a wrapped file in a way it cannot cut."""


class LateRow(RuntimeError):
    """A row or a date past the cut's last day."""


def _day(x: Any) -> date:
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, date):
        return x
    return date.fromisoformat(str(x)[:10])


@dataclass
class Read:
    file: str
    kind: str                       # "cut" or "passthrough"
    rows: int | None = None
    last_key: str | None = None


@dataclass
class CutLog:
    """What a cut saw: every data read (cut or passed through) and every refusal."""
    last: date
    root: Path
    reads: list[Read] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)

    def files_read(self, kind: str | None = None) -> list[str]:
        return sorted({r.file for r in self.reads if kind is None or r.kind == kind})

    def problems(self, want: Sequence[str] = ()) -> list[str]:
        """Refusals seen; a late key kept; a wanted file (a `WRAPPED` pattern or path) never read through the cut."""
        out = [f"refused: {x}" for x in self.refused]
        out += [f"{r.file}: a row past {self.last} kept" for r in self.reads
                if r.kind == "cut" and r.last_key is not None and r.last_key > self.last.isoformat()]
        got = self.files_read("cut")
        out += [f"{w}: never read through the cut" for w in want if not any(fnmatch.fnmatchcase(g, w) for g in got)]
        return out


def bases(root: Path) -> tuple[tuple[Path, str], ...]:
    """Where the vendored tree's files may be seen from: the root as written and its real path, and each guarded
    folder's real path -- in a worktree or a clean checkout `data/bars` and `data/atlas` are directory junctions into
    the main tree (CLAUDE.md), and a path through them resolves to the junction's target, not under the root."""
    root = Path(root)
    out = [(Path(os.path.abspath(root)), ""), (Path(os.path.realpath(root)), "")]
    out += [(Path(os.path.realpath(root / g)), g + "/") for g in GUARDED]
    return tuple(dict.fromkeys(out))


def _rel(path: Any, root: Path, known: tuple[tuple[Path, str], ...] | None = None) -> str | None:
    """The path relative to the vendored tree, POSIX (through a junction too), or None outside it."""
    if not isinstance(path, (str, Path)):
        return None
    try:
        cands = (Path(os.path.abspath(path)), Path(os.path.realpath(path)))
    except (ValueError, OSError):
        return None
    for base, prefix in (known if known is not None else bases(root)):
        for p in cands:
            try:
                return prefix + p.relative_to(base).as_posix()
            except ValueError:
                continue
    return None


def wrapped_key(rel: str) -> str | None:
    for pat, key in WRAPPED.items():
        if fnmatch.fnmatchcase(rel, pat):
            return key
    return None


def is_passthrough(rel: str) -> bool:
    return any(fnmatch.fnmatchcase(rel, pat) for pat in PASSTHROUGH)


def is_guarded(rel: str) -> bool:
    return any(rel == g or rel.startswith(g + "/") for g in GUARDED)


def _with_cut(filters: Any, key: str, last: str) -> list:
    """`filters` (None, a list of tuples, or a list of lists of tuples) with `key <= last` added to every conjunction."""
    term = (key, "<=", last)
    if not filters:
        return [term]
    if all(isinstance(f, tuple) for f in filters):
        return [*filters, term]
    if all(isinstance(f, list) for f in filters):
        return [[*conj, term] for conj in filters]
    raise UnwrappedRead(f"filters of an unknown shape {filters!r}: the cut cannot be added")


def switched_off() -> dict[str, str]:
    """What a manifest prints: every vendored check switched off under the cut (none at this commit)."""
    return dict(SWITCHED_OFF)


@contextlib.contextmanager
def cut(last: Any = LAST_DAY, *, root: Path | str = VENDOR_STAGE2) -> Iterator[CutLog]:
    """Every data read inside the block cut at `last` or refused (the module's docstring). `last` may not pass the
    search years' last day."""
    import pandas as pd

    last_d = _day(last)
    if last_d > LAST_DAY:
        raise LateRow(f"REFUSED ({TASK}): a cut at {last_d} passes the search years' last day {LAST_DAY}")
    if last_d < FIRST_DAY:
        raise ValueError(f"a cut at {last_d} is before the development window opens on {FIRST_DAY}")
    root = Path(root)
    log = CutLog(last_d, root)
    known = bases(root)
    iso = last_d.isoformat()
    real_parquet = pd.read_parquet
    real_open, real_io_open = builtins.open, io.open
    inside = threading.local()

    def refuse(why: str):
        log.refused.append(why)
        raise UnwrappedRead(f"REFUSED ({TASK}): {why} -- the search cut reads only {sorted(WRAPPED)} as data")

    def read_parquet(path, *args, **kw):
        rel = _rel(path, root, known)
        key = wrapped_key(rel) if rel is not None else None
        if key is None:
            refuse(f"a parquet read of {rel or path!r}, not a wrapped file")
        import pyarrow.parquet as pq

        names = list(pq.read_schema(Path(path)).names)
        if key not in names:
            refuse(f"{rel} has no key column {key!r}")
        kw["filters"] = _with_cut(kw.get("filters"), key, iso)
        inside.on = getattr(inside, "on", 0) + 1
        try:
            df = real_parquet(path, *args, **kw)
        finally:
            inside.on -= 1
        last_key = None
        if key in df.columns and len(df):
            late = df[key].astype(str) > iso
            if late.any():
                raise LateRow(f"REFUSED ({TASK}): {rel}: {int(late.sum())} rows past {iso} came through the filter")
            last_key = str(df[key].astype(str).max())
        log.reads.append(Read(rel, "cut", int(len(df)), last_key))
        return df

    def guard_open(file, *args, **kw):
        if not getattr(inside, "on", 0):
            rel = _rel(file, root, known)
            if rel is not None and is_guarded(rel):
                if is_passthrough(rel):
                    log.reads.append(Read(rel, "passthrough"))
                else:
                    refuse(f"a file opened under the data folders: {rel}")
        return real_open(file, *args, **kw)

    def guard_io_open(file, *args, **kw):
        if not getattr(inside, "on", 0):
            rel = _rel(file, root, known)
            if rel is not None and is_guarded(rel):
                if is_passthrough(rel):
                    log.reads.append(Read(rel, "passthrough"))
                else:
                    refuse(f"a file opened under the data folders: {rel}")
        return real_io_open(file, *args, **kw)

    pd.read_parquet = read_parquet
    builtins.open = guard_open
    io.open = guard_io_open
    try:
        yield log
    finally:
        pd.read_parquet = real_parquet
        builtins.open = real_open
        io.open = real_io_open


def check_dates(dates: Sequence[Any], last: Any = LAST_DAY, what: str = "the job") -> None:
    """The backstop: every date of a job (or a block list's days) at or before the cut's last day."""
    late = [d for d in dates if _day(d) > _day(last)]
    if late:
        raise LateRow(f"REFUSED ({TASK}): {what} holds {len(late)} date(s) past {_day(last)} (first {late[0]})")


def wrapped_files(root: Path | str = VENDOR_STAGE2, *, bars: bool = False, roots: Sequence[str] = ("NQ",)) -> list[Path]:
    """The wrapped files that exist under `root` (the bars' only when `bars`), for the reader's door."""
    root = Path(root)
    out = [root / p for p in WRAPPED if "*" not in p and (root / p).is_file()]
    if bars:
        out += [root / "data" / "bars" / r / "bars.parquet" for r in roots]
    return out


def authorise(*, purpose: str, declaration: str, what: str, last: Any = LAST_DAY, bars: bool = False,
              root: Path | str = VENDOR_STAGE2) -> R.Authorisation:
    """`extended.reader.authorise_engine_read` for the cut's span and the wrapped files, before the build; refused if
    the authorisation reaches the judged block (it cannot, at a cut inside the search years)."""
    last_d = _day(last)
    if last_d > LAST_DAY:
        raise LateRow(f"REFUSED ({TASK}): a cut at {last_d} passes {LAST_DAY}")
    a = R.authorise_engine_read(FIRST_DAY, last_d, files=wrapped_files(root, bars=bars), what=what, purpose=purpose,
                                declaration=declaration)
    if a.judged:
        raise LateRow(f"REFUSED ({TASK}): the authorisation reaches the judged block")
    return a


__all__ = ["TASK", "LAST_DAY", "FIRST_DAY", "WRAPPED", "PASSTHROUGH", "GUARDED", "SWITCHED_OFF", "UnwrappedRead",
           "LateRow", "Read", "CutLog", "wrapped_key", "is_passthrough", "is_guarded", "switched_off", "cut",
           "check_dates", "wrapped_files", "authorise"]
