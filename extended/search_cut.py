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
from typing import Any, Iterator, Mapping, Sequence

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
#: vendored checks switched off under the cut, each `name: reason (row)`
SWITCHED_OFF: dict[str, str] = {
    "rc_dev_test.trade_problems": (
        "screen-row and whole-window hash check replaced on cut rows only by I-1 search-year sub-hash comparison; "
        "whole-window builds keep it (E-286)"
    ),
}


class UnwrappedRead(RuntimeError):
    """A builder read a data file the cut does not wrap, or a wrapped file in a way it cannot cut."""


class LateRow(RuntimeError):
    """A row or a date past the cut's last day."""


class ConstantsMismatch(RuntimeError):
    """Registered-constants file hash, schema, or I-1 sub-hash check failed."""


class CalendarMismatch(RuntimeError):
    """The cut's A1 day list does not equal Q-197's pinned search calendar date for date (rm-6)."""


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
    """What a cut saw: every data read (cut or passed through), every refusal, and pass-through audit fields."""
    last: date
    root: Path
    reads: list[Read] = field(default_factory=list)
    refused: list[str] = field(default_factory=list)
    passed_through: list[str] = field(default_factory=list)
    computed_from_cut: list[str] = field(default_factory=list)
    switched_off_used: list[str] = field(default_factory=list)
    constants_file: str | None = None
    constants_sha256: str | None = None
    files_sha256: dict[str, str] = field(default_factory=dict)

    def files_read(self, kind: str | None = None) -> list[str]:
        return sorted({r.file for r in self.reads if kind is None or r.kind == kind})

    def manifest_summary(self) -> dict[str, Any]:
        """Audit record for manifests: passed-through statistics, cut-computed statistics, switched-off checks, files."""
        return {
            "last_day": self.last.isoformat(),
            "passed_through": sorted(set(self.passed_through)),
            "computed_from_cut": sorted(set(self.computed_from_cut)),
            "switched_off_used": sorted(set(self.switched_off_used)),
            "constants_file": self.constants_file,
            "constants_sha256": self.constants_sha256,
            "files_cut": self.files_read("cut"),
            "files_passthrough": self.files_read("passthrough"),
            "files_sha256": dict(sorted(self.files_sha256.items())),
        }

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
    """What a manifest prints: every vendored check switched off under the cut."""
    return dict(SWITCHED_OFF)


def load_constants(path: Path | str, *, expected_sha256: str) -> dict[str, dict[str, Any]]:
    """Load H4's registered-constants CSV, refusing unless its raw sha256 equals BOTH its manifest and `expected_sha256`."""
    import csv
    import hashlib
    import json

    p = Path(path)
    if not p.is_file():
        raise ConstantsMismatch(f"REFUSED ({TASK}): missing registered-constants file {p}")
    raw = p.read_bytes()
    file_sha = hashlib.sha256(raw).hexdigest()
    if file_sha != expected_sha256:
        raise ConstantsMismatch(f"REFUSED ({TASK}): {p.name} sha256 {file_sha} != expected {expected_sha256}")
    side = Path(str(p) + ".manifest.json")
    if not side.is_file():
        raise ConstantsMismatch(f"REFUSED ({TASK}): {p.name} missing sidecar manifest")
    man = json.loads(side.read_text(encoding="utf-8"))
    if man.get("sha256") != file_sha:
        raise ConstantsMismatch(f"REFUSED ({TASK}): {p.name} sha256 {file_sha} != manifest {man.get('sha256')}")
    with p.open("r", encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        rows = list(rd)
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        d = str(r["design"])
        slots_txt = str(r.get("offered_marks_slots", "")).strip()
        slots = tuple(int(tok) for tok in slots_txt.split()) if slots_txt else ()
        if len(slots) != int(r["marks_count"]):
            raise ConstantsMismatch(f"REFUSED ({TASK}): {d} marks_count != parsed slots")
        if str(r["search_last_date"]) > LAST_DAY.isoformat():
            raise ConstantsMismatch(f"REFUSED ({TASK}): {d} search_last_date passes {LAST_DAY}")
        out[d] = {
            "design": d,
            "cell": str(r["cell"]),
            "stop_ticks": int(r["stop_ticks"]),
            "busiest_day": int(r["busiest_day"]),
            "capacity": int(r["capacity"]),
            "marks_count": int(r["marks_count"]),
            "offered_marks": slots,
            "search_trades": int(r["search_trades"]),
            "search_first_date": str(r["search_first_date"]),
            "search_last_date": str(r["search_last_date"]),
            "search_trades_sha256": str(r["search_trades_sha256"]),
            "source_file": str(r["source_file"]),
            "source_sha256": str(r["source_sha256"]),
            "file_sha256": file_sha,
        }
    for req in ("p14", "p15", "p16"):
        if req not in out:
            raise ConstantsMismatch(f"REFUSED ({TASK}): registered constants missing design {req!r}")
    return out


def trades_subhash(trades: Any, *, last: Any = LAST_DAY) -> str:
    """Exact `rc_dev_test.trades_hash` form on cut trades, refusing any trading day past `last`."""
    import hashlib
    import pandas as pd

    if not isinstance(trades, pd.DataFrame) or "date" not in trades.columns:
        raise ConstantsMismatch(f"REFUSED ({TASK}): trades must be a DataFrame with a 'date' column")
    last_iso = _day(last).isoformat()
    if len(trades):
        late = trades["date"].astype(str) > last_iso
        if late.any():
            raise LateRow(f"REFUSED ({TASK}): trades hold {int(late.sum())} row(s) past {last_iso}")
    cols = sorted(trades.columns)
    h = pd.util.hash_pandas_object(trades[cols].reset_index(drop=True), index=False).to_numpy()
    return hashlib.sha256(h.tobytes() + "|".join(cols).encode()).hexdigest()


def verify_subhash(design: str, trades: Any, constants: Mapping[str, Mapping[str, Any]], *, last: Any = LAST_DAY) -> str:
    """I-1: check cut trades against the registered-constants search-year sub-hash and count (refuses on mismatch)."""
    if design not in constants:
        raise ConstantsMismatch(f"REFUSED ({TASK}): unknown design {design!r} for I-1 sub-hash check")
    got_hash = trades_subhash(trades, last=last)
    reg = constants[design]
    if int(len(trades)) != int(reg["search_trades"]):
        raise ConstantsMismatch(
            f"REFUSED (I-1): {design} cut trade count {len(trades)} != registered {reg['search_trades']}"
        )
    if got_hash != str(reg["search_trades_sha256"]):
        raise ConstantsMismatch(
            f"REFUSED (I-1): {design} cut trades sub-hash {got_hash} != registered {reg['search_trades_sha256']}"
        )
    return got_hash


def check_calendar(dates: Sequence[Any], *, calendar_path: Path | str | None = None, last: Any = LAST_DAY) -> list[str]:
    """rm-6: refuse unless `dates` (the cut's A1 day list) equals Q-197's pinned search calendar date for date up to `last`."""
    from extended import search_calendar as SCAL

    last_d = _day(last)
    if last_d > LAST_DAY:
        raise LateRow(f"REFUSED ({TASK}): calendar check at {last_d} passes {LAST_DAY}")
    cal = SCAL.load_search_calendar(calendar_path)
    want = [d for d in cal.dates if d <= last_d.isoformat()]
    got = [_day(d).isoformat() for d in dates]
    if got != want:
        raise CalendarMismatch(
            f"REFUSED (rm-6): cut A1 day list ({len(got)} days) != pinned search calendar ({len(want)} days) "
            f"up to {last_d}"
        )
    return got


@contextlib.contextmanager
def pass_through(
    design: str,
    constants_path: Path | str,
    *,
    expected_sha256: str,
    last: Any = LAST_DAY,
    root: Path | str = VENDOR_STAGE2,
    switch_off_trade_problems: bool = True,
    modules: Mapping[str, Any] | None = None,
) -> Iterator[CutLog]:
    """Pass-through mode of the search cut (H4 Appendix C, B-2, E-286): inside `cut(last, root)`, replaces whole-window
    statistics a registered builder would otherwise re-resolve on cut rows (`a3_brk30.capacity`, and for P-15/P-16
    `resolved_coin.offered_marks`) with the pinned values from `constants_path` (checked against `expected_sha256`),
    and optionally switches off `rc_dev_test.trade_problems` (recorded in `SWITCHED_OFF` under E-286) on cut rows only.

    `modules` may supply synthetic stand-in modules (`a3_brk30`, `resolved_coin`, `rc_dev_test`) for unit testing
    without importing the vendored engine.
    """
    if design not in ("p14", "p15", "p16"):
        raise ConstantsMismatch(f"REFUSED ({TASK}): pass_through design must be p14, p15, or p16, got {design!r}")
    constants = load_constants(constants_path, expected_sha256=expected_sha256)
    reg = constants[design]

    if modules is not None:
        mod_b = modules.get("a3_brk30")
        mod_rc = modules.get("resolved_coin")
        mod_d = modules.get("rc_dev_test")
    else:
        import a3_brk30 as mod_b
        import rc_dev_test as mod_d
        from propedge.research import resolved_coin as mod_rc

    with cut(last=last, root=root) as log:
        log.constants_file = str(Path(constants_path))
        log.constants_sha256 = str(reg["file_sha256"])
        log.computed_from_cut.append("search_year_trades_and_bounds")
        saved: list[tuple[Any, str, Any]] = []

        try:
            if mod_b is not None and hasattr(mod_b, "capacity"):
                real_cap = mod_b.capacity
                saved.append((mod_b, "capacity", real_cap))
                reg_cap = int(reg["capacity"])

                def _pt_capacity(t, fcfg):
                    cut_cap = int(real_cap(t, fcfg))
                    if cut_cap > reg_cap:
                        raise ConstantsMismatch(
                            f"REFUSED ({TASK}): {design} cut capacity {cut_cap} > registered capacity {reg_cap}"
                        )
                    log.passed_through.append(f"{design}.capacity={reg_cap}")
                    return reg_cap

                mod_b.capacity = _pt_capacity

            if design in ("p15", "p16") and mod_rc is not None and hasattr(mod_rc, "offered_marks"):
                real_marks = mod_rc.offered_marks
                saved.append((mod_rc, "offered_marks", real_marks))
                reg_stop = int(reg["stop_ticks"])
                reg_marks = list(reg["offered_marks"])

                def _pt_offered_marks(table, stop_ticks):
                    if int(stop_ticks) == reg_stop:
                        log.passed_through.append(f"{design}.offered_marks(stop={reg_stop},n={len(reg_marks)})")
                        return list(reg_marks)
                    return real_marks(table, stop_ticks)

                mod_rc.offered_marks = _pt_offered_marks

            if design in ("p15", "p16") and switch_off_trade_problems and mod_d is not None and hasattr(mod_d, "trade_problems"):
                real_tp = mod_d.trade_problems
                saved.append((mod_d, "trade_problems", real_tp))

                def _pt_trade_problems(*args, **kwargs):
                    log.switched_off_used.append("rc_dev_test.trade_problems")
                    return []

                mod_d.trade_problems = _pt_trade_problems

            yield log
        finally:
            for mod, attr, orig in reversed(saved):
                setattr(mod, attr, orig)


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
           "LateRow", "ConstantsMismatch", "CalendarMismatch", "Read", "CutLog", "wrapped_key", "is_passthrough",
           "is_guarded", "switched_off", "load_constants", "trades_subhash", "verify_subhash", "check_calendar",
           "cut", "pass_through", "check_dates", "wrapped_files", "authorise"]
